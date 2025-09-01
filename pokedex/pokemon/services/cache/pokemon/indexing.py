from ..core.indexing import (
    get_total_count as _get_total_count,
    iter_index_ids as _iter_index_ids,
)


def get_pokedex_count() -> int:
    return _get_total_count("pokemon")


def iter_index_ids(batch_size: int):
    return _iter_index_ids("pokemon", batch_size)