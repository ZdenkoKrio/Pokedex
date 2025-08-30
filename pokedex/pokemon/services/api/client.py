from __future__ import annotations

from datetime import timedelta
from typing import Dict, Optional

from pokemon.models import ApiResourceCache
from .session import get_session
from .cache import is_fresh, conditional_headers, bump_expiry, persist_row


DEFAULT_TTL = timedelta(hours=24)
DEFAULT_TIMEOUT = 10.0  # seconds


def get_json(
    url: str,
    ttl: timedelta = DEFAULT_TTL,
    timeout: float = DEFAULT_TIMEOUT,
    extra_headers: Optional[Dict[str, str]] = None,
) -> dict:
    """
    Fetch JSON for `url` using a DB-backed cache with TTL and HTTP validators.

    Behavior
    --------
    1) If a cache row exists and is fresh, return it.
    2) Otherwise, issue a conditional GET (ETag/Last-Modified when available).
       - 304 → bump expiry and return cached payload.
       - 200 → replace payload and validators, return new payload.

    Raises
    ------
    requests.HTTPError
        For non-2xx/304 responses (after retries at the adapter level).
    json.JSONDecodeError
        If a 200 response does not contain valid JSON.
    """
    row: Optional[ApiResourceCache]

    try:
        row = ApiResourceCache.objects.get(url=url)
        if is_fresh(row):
            return row.payload

    except ApiResourceCache.DoesNotExist:
        row = None

    headers = conditional_headers(row)
    if extra_headers:
        headers.update(extra_headers)

    r = get_session().get(url, timeout=timeout, headers=headers)

    # Not modified → extend TTL and return cached
    if r.status_code == 304 and row:
        bump_expiry(row, ttl)
        return row.payload

    r.raise_for_status()
    data = r.json()
    saved = persist_row(row, url, data, r.headers, ttl)
    return saved.payload