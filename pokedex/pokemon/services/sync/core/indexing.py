from __future__ import annotations
from typing import Iterable, List, Sequence
from pokemon.services.api import get_json, url


def extract_ids_from_index(results: Sequence[dict]) -> List[int]:
    """Parse integer IDs from typical PokeAPI index result rows."""
    return [int(row["url"].rstrip("/").split("/")[-1]) for row in results]


def get_total_count(resource: str) -> int:
    """Cheap total count via `?limit=1` on a resource path (e.g., 'pokemon')."""
    data = get_json(url(resource) + "?limit=1")
    return int(data.get("count", 0) or 0)


def iter_index_ids(resource: str, batch_size: int) -> Iterable[int]:
    """Yield all integer IDs by paging a PokeAPI index endpoint."""
    count = get_total_count(resource)
    offset = 0
    while offset < count:
        data = get_json(url(resource) + f"?offset={offset}&limit={batch_size}")
        results = data.get("results", [])
        if not results:
            break
        for item_id in extract_ids_from_index(results):
            yield item_id
        offset += batch_size