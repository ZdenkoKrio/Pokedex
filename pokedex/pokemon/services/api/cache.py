from __future__ import annotations
from datetime import timedelta
from typing import Dict, Optional
from django.utils import timezone
from pokemon.models import ApiResourceCache


def _now():
    return timezone.now()


def is_fresh(row: ApiResourceCache, at: Optional[timezone.datetime] = None) -> bool:
    """
    Return True if the cached row is still fresh with respect to `expires_at`.
    """
    at = at or _now()
    return not row.expires_at or row.expires_at > at


def conditional_headers(row: Optional[ApiResourceCache]) -> Dict[str, str]:
    """
    Build conditional request headers (If-None-Match / If-Modified-Since)
    from cached validators, if available.
    """
    if not row:
        return {}

    headers: Dict[str, str] = {}

    if row.etag:
        headers["If-None-Match"] = row.etag

    if row.last_modified:
        headers["If-Modified-Since"] = row.last_modified

    return headers


def bump_expiry(row: ApiResourceCache, ttl: timedelta) -> None:
    """
    Extend the cache row validity without mutating the payload/validators.
    """
    row.expires_at = _now() + ttl
    row.save(update_fields=["expires_at"])


def persist_row(
    row: Optional[ApiResourceCache],
    url: str,
    payload: dict,
    headers: Dict[str, str],
    ttl: timedelta,
) -> ApiResourceCache:
    """
    Create or update the cache row with a new payload and HTTP validators.
    """
    expires = _now() + ttl
    etag = headers.get("ETag", "")
    last_modified = headers.get("Last-Modified", "")

    if row:
        row.payload = payload
        row.etag = etag
        row.last_modified = last_modified
        row.expires_at = expires
        row.save(update_fields=["payload", "etag", "last_modified", "expires_at"])
        return row

    return ApiResourceCache.objects.create(
        url=url,
        payload=payload,
        etag=etag,
        last_modified=last_modified,
        expires_at=expires,
    )