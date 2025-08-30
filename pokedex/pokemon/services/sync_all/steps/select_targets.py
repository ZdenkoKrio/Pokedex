from __future__ import annotations
from typing import List, Set, Tuple
from pokemon.models import PokemonCache


def select_targets(all_ids: List[int], only_missing: bool) -> Tuple[List[int], int]:
    """
    Choose target IDs for sync.

    Parameters
    ----------
    all_ids : list[int]
    only_missing : bool
        If True, skip IDs already present in DB.

    Returns
    -------
    (targets, skipped) : (list[int], int)
    """
    existing: Set[int] = set(PokemonCache.objects.values_list("pokeapi_id", flat=True))
    targets = [pid for pid in all_ids if (pid not in existing or not only_missing)]
    skipped = len(all_ids) - len(targets)
    return targets, skipped