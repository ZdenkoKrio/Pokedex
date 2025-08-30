from __future__ import annotations
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

from ..constants import ProgressFn, LogFn, PROGRESS_EVERY_N
from ..db_utils import missing_after_chunk
from ..progress import report_progress
from ..worker import submit_chunk


def run_main_pass(
    targets: List[int],
    *,
    workers: int,
    batch_size: int,
    sleep_between_batches: float,
    attempts: int,
    progress: ProgressFn,
    logger: LogFn,
    t0: float,
) -> Tuple[int, List[int], int]:
    """
    Execute the main parallel pass.

    Returns
    -------
    synced : int
        Number of successful upserts.
    failed_ids : list[int]
        IDs still missing in DB after this pass.
    done : int
        Items processed (for progress).
    """
    if not targets:
        return 0, [], 0

    synced = 0
    done = 0
    failed_ids: List[int] = []
    batches = max(1, (len(targets) + batch_size - 1) // batch_size)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for bi in range(batches):
            chunk = targets[bi * batch_size : (bi + 1) * batch_size]
            futures = submit_chunk(ex, chunk, attempts=attempts, logger=logger)

            for fut in as_completed(futures):
                if fut.result():
                    synced += 1
                done += 1
                if progress and (done % PROGRESS_EVERY_N == 0):
                    report_progress(
                        progress,
                        "sync",
                        len(targets),
                        done,
                        synced,
                        failed_count=len(failed_ids),
                        skipped=0,
                        batch=bi + 1,
                        batches=batches,
                        t0=t0,
                    )

            # precise accounting of what still isn't in DB for this chunk
            missing_now = missing_after_chunk(chunk)
            if missing_now:
                failed_ids.extend(list(missing_now))

            if sleep_between_batches:
                time.sleep(sleep_between_batches)

            report_progress(
                progress,
                "sync",
                len(targets),
                done,
                synced,
                failed_count=len(failed_ids),
                skipped=0,
                batch=bi + 1,
                batches=batches,
                t0=t0,
            )

    return synced, failed_ids, done