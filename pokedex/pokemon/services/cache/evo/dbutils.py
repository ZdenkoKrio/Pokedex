from __future__ import annotations
"""
Thin DB adapters for EvolutionChainCache.
"""

from typing import Sequence, Set
from pokemon.models import EvolutionChainCache
from ..core.dbutils import db_have_values


def db_have_chain_ids(ids: Sequence[int]) -> Set[int]:
    return db_have_values(EvolutionChainCache, "chain_id", ids)


def missing_after_chunk(chunk: Sequence[int]) -> Set[int]:
    return set(chunk) - db_have_chain_ids(chunk)