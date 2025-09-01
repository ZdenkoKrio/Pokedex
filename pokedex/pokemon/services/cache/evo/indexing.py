from __future__ import annotations
"""
Index enumeration helpers for the /evolution-chain endpoint.
"""

from typing import Iterable
from ..core.indexing import (
    get_total_count as _get_total_count,
    iter_index_ids as _iter_index_ids,
)


def get_chain_count() -> int:
    return _get_total_count("evolution-chain")


def iter_chain_ids(batch_size: int) -> Iterable[int]:
    return _iter_index_ids("evolution-chain", batch_size)