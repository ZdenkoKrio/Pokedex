from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Set

from ..constants import ProgressFn, LogFn
from ..db_utils import db_have_ids
from ..progress import report_progress
from ..worker import submit_chunk


def run_retry_passes(
    failed_ids: List[int],
    *,
    workers: int,
    attempts: int,
    rounds: int,
    progress: ProgressFn,
    logger: LogFn,
    t0: float,
) -> Tuple[int, List[int]]:
    """
    Run N smaller retry rounds.

    Returns
    -------
    add_synced : int
        Extra successes reached during retries.
    remaining : list[int]
        IDs still missing after all retry rounds.
    """
    add_synced = 0
    remaining = list(failed_ids)

    for round_idx in range(1, rounds + 1):
        if not remaining:
            break

        retry_ids = remaining
        remaining = []

        with ThreadPoolExecutor(max_workers=max(1, workers // 2)) as ex:
            futures = submit_chunk(ex, retry_ids, attempts=max(1, attempts // 2), logger=logger)
            for fut in as_completed(futures):
                if fut.result():
                    add_synced += 1

        still_missing: Set[int] = set(retry_ids) - db_have_ids(retry_ids)
        if still_missing:
            remaining.extend(list(still_missing))

        report_progress(
            progress,
            f"retry-{round_idx}",
            len(retry_ids),
            len(retry_ids),
            synced=len(retry_ids) - len(still_missing),
            failed_count=len(still_missing),
            skipped=0,
            batch=round_idx,
            batches=rounds,
            t0=t0,
        )

    return add_synced, remaining