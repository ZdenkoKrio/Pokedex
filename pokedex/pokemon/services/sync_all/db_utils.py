from __future__ import annotations
"""
Thin DB helpers used by the bulk sync.
"""

from typing import Sequence, Set
from django.db.models import QuerySet
from pokemon.models import PokemonCache


def db_have_ids(ids: Sequence[int]) -> Set[int]:
    """Return the subset of given IDs that already exist in DB."""
    if not ids:
        return set()
    qs: QuerySet = PokemonCache.objects.filter(
        pokeapi_id__in=ids
    ).values_list("pokeapi_id", flat=True)
    return set(qs)


def missing_after_chunk(chunk: Sequence[int]) -> Set[int]:
    """Compute which IDs from the chunk are still missing in DB."""
    return set(chunk) - db_have_ids(chunk)