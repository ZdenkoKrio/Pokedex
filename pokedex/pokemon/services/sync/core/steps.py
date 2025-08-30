from __future__ import annotations
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, Sequence, Tuple, Set, Optional, Dict, Any

ProgressFn = Optional[Callable[[Dict[str, Any]], None]]


def enumerate_ids(iter_ids: Callable[[int], Iterable[int]],
                  batch_size: int,
                  progress: ProgressFn) -> Tuple[List[int], float]:
    """
    Execute index paging callback and return (ids, perf_counter_start).
    """
    t0 = time.perf_counter()
    ids = list(iter_ids(batch_size=batch_size))
    if progress:
        progress({"phase": "index", "total": len(ids), "done": len(ids)})
    return ids, t0


def select_targets(all_ids: List[int],
                   existing_ids: Set[int],
                   only_missing: bool) -> Tuple[List[int], int]:
    """
    Decide which IDs to process; returns (targets, skipped_count).
    """
    targets = [i for i in all_ids if (i not in existing_ids or not only_missing)]
    return targets, (len(all_ids) - len(targets))


def run_main_pass(
    targets: List[int],
    *,
    workers: int,
    batch_size: int,
    sleep_between_batches: float,
    submit_chunk: Callable[[ThreadPoolExecutor, Sequence[int]], Sequence],  # returns futures
    progress: ProgressFn,
    metric_key: str,  # e.g. "synced" or "ok"
    progress_every_n: int,
    missing_after_chunk: Callable[[Sequence[int]], Set[int]],
    t0: float,
) -> Tuple[int, List[int], int]:
    """
    Execute the main parallel pass and return (good_count, failed_ids, done_count).
    """
    if not targets:
        return 0, [], 0

    done = 0
    good = 0
    failed_ids: List[int] = []
    batches = max(1, (len(targets) + batch_size - 1) // batch_size)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for bi in range(batches):
            chunk = targets[bi * batch_size : (bi + 1) * batch_size]
            futures = submit_chunk(ex, chunk)

            optimistic = 0
            for fut in as_completed(futures):
                if fut.result():
                    optimistic += 1
                done += 1

                if progress and (done % progress_every_n == 0):
                    _report(progress, phase="sync", total=len(targets), done=done,
                            good=good + optimistic, failed=len(failed_ids),
                            skipped=0, batch=bi + 1, batches=batches, t0=t0,
                            metric_key=metric_key)

            # exact DB accounting after the batch
            missing_now = missing_after_chunk(chunk)
            good += len(chunk) - len(missing_now)
            if missing_now:
                failed_ids.extend(list(missing_now))

            if sleep_between_batches:
                time.sleep(sleep_between_batches)

            _report(progress, phase="sync", total=len(targets), done=done,
                    good=good, failed=len(failed_ids), skipped=0,
                    batch=bi + 1, batches=batches, t0=t0, metric_key=metric_key)

    return good, failed_ids, done


def run_retry_passes(
    failed_ids: List[int],
    *,
    workers: int,
    rounds: int,
    submit_chunk_retry: Callable[[ThreadPoolExecutor, Sequence[int]], Sequence],
    have_in_db: Callable[[Sequence[int]], Set[int]],
    progress: ProgressFn,
    metric_key: str,  # e.g. "synced" or "ok"
    t0: float,
) -> Tuple[int, List[int]]:
    """
    Run N smaller retry rounds; return (additional_good, remaining_ids).
    """
    add_good = 0
    remaining = list(failed_ids)

    for round_idx in range(1, rounds + 1):
        if not remaining:
            break

        retry_ids = remaining
        remaining = []

        with ThreadPoolExecutor(max_workers=max(1, workers // 2)) as ex:
            futures = submit_chunk_retry(ex, retry_ids)
            for fut in as_completed(futures):
                if fut.result():
                    add_good += 1

        still_missing = set(retry_ids) - have_in_db(retry_ids)
        if still_missing:
            remaining.extend(list(still_missing))

        # per-round report
        _report(progress, phase=f"retry-{round_idx}", total=len(retry_ids),
                done=len(retry_ids), good=len(retry_ids) - len(still_missing),
                failed=len(still_missing), skipped=0, batch=round_idx,
                batches=rounds, t0=t0, metric_key=metric_key)

    return add_good, remaining


def _report(progress: ProgressFn, *, phase: str, total: int, done: int, good: int,
            failed: int, skipped: int, batch: int, batches: int, t0: float,
            metric_key: str) -> None:
    """
    Internal progress reporter that emits `metric_key` with the `good` count.
    """
    if not progress:
        return

    elapsed = time.perf_counter() - t0
    rate = (done / elapsed) if elapsed > 0 else 0.0
    remaining = max(0, total - done)
    eta = (remaining / rate) if rate > 0 else 0.0
    payload = {
        "phase": phase,
        "total": total,
        "done": done,
        metric_key: good,
        "failed": failed,
        "skipped": skipped,
        "batch": batch,
        "batches": batches,
        "rate": rate,
        "eta": eta,
    }
    progress(payload)