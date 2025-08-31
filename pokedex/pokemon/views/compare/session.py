from __future__ import annotations
from typing import List, Iterable
from django.http import HttpRequest

from .constants import SESSION_KEY


def _unique_preserve_order(items: Iterable[int]) -> List[int]:
    """
    Deduplicate list while preserving order.
    """
    seen = set()
    out: List[int] = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def get_session_list(request: HttpRequest) -> List[int]:
    """
    Safely load list of Pokémon IDs from session.
    Always returns integers, deduplicated, order-preserved.
    """
    raw = request.session.get(SESSION_KEY) or []
    try:
        ids = [int(x) for x in raw]
    except Exception:
        ids = []
    return _unique_preserve_order(ids)


def save_session_list(request: HttpRequest, ids: Iterable[int]) -> None:
    """
    Save list of Pokémon IDs into session.
    Deduplicates and preserves order.
    """
    request.session[SESSION_KEY] = _unique_preserve_order(int(i) for i in ids)
    request.session.modified = True