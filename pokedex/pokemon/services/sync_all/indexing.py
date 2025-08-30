from __future__ import annotations
"""
Index enumeration helpers for /pokemon endpoint.
"""

from typing import Iterable, List, Sequence
from pokemon.services.api import get_json, url


def extract_ids_from_index(results: Sequence[dict]) -> List[int]:
    """Pull integer Pokémon IDs out of index rows (by parsing trailing URL path)."""
    return [int(row["url"].rstrip("/").split("/")[-1]) for row in results]


def get_pokedex_count() -> int:
    """Cheap way to get total count using `?limit=1`."""
    data = get_json(url("pokemon") + "?limit=1")
    return int(data.get("count", 0) or 0)


def iter_index_ids(batch_size: int) -> Iterable[int]:
    """
    Yield all Pokémon IDs by paging the index endpoint.

    Requests are cached by our API layer, so repeated calls are cheap
    (unless TTL expired).
    """
    count = get_pokedex_count()
    offset = 0
    while offset < count:
        data = get_json(url("pokemon") + f"?offset={offset}&limit={batch_size}")
        results = data.get("results", [])
        if not results:
            break
        for pid in extract_ids_from_index(results):
            yield pid
        offset += batch_size