from __future__ import annotations
import time
from typing import List, Tuple
from ..constants import ProgressFn
from ..indexing import iter_index_ids


def enumerate_ids(batch_size: int, progress: ProgressFn) -> Tuple[List[int], float]:
    """
    Page the PokeAPI index and collect all Pokémon IDs.

    Returns
    -------
    (ids, t0) : (list[int], float)
        The IDs and perf counter start time for later ETA math.
    """
    t0 = time.perf_counter()
    ids = list(iter_index_ids(batch_size=batch_size))
    if progress:
        progress({"phase": "index", "total": len(ids), "done": len(ids)})
    return ids, t0