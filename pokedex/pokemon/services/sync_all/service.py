from __future__ import annotations
"""
Bulk Pokédex sync orchestrator composed from small, testable steps.
"""

import time

from .constants import (
    PAGE_SIZE_DEFAULT,
    MAX_WORKERS_DEFAULT,
    SECOND_PASSES,
    UPSERT_ATTEMPTS,
    ProgressFn,
    LogFn,
)
from .steps.enumerate_ids import enumerate_ids
from .steps.select_targets import select_targets
from .steps.run_main_pass import run_main_pass
from .steps.run_retry_passes import run_retry_passes


def sync_all_pokemon(
    workers: int = MAX_WORKERS_DEFAULT,
    batch_size: int = PAGE_SIZE_DEFAULT,
    sleep_between_batches: float = 0.0,
    only_missing: bool = True,
    progress: ProgressFn = None,
    *,
    logger: LogFn = None,
) -> dict:
    """
    Fetch/refresh ALL Pokémon into the local DB cache (without evolution chains).
    Does NOT create taxonomies; missing ones are only reported to `logger`.
    """
    all_ids, t0 = enumerate_ids(batch_size, progress)
    total = len(all_ids)
    if total == 0:
        return {"synced": 0, "skipped": 0, "failed": 0, "total": 0, "elapsed": 0.0}

    targets, skipped = select_targets(all_ids, only_missing)
    if not targets:
        elapsed = round(time.perf_counter() - t0, 2)
        return {"synced": 0, "skipped": skipped, "failed": 0, "total": total, "elapsed": elapsed}

    synced, failed_ids, _done = run_main_pass(
        targets,
        workers=workers,
        batch_size=batch_size,
        sleep_between_batches=sleep_between_batches,
        attempts=UPSERT_ATTEMPTS,
        progress=progress,
        logger=logger,
        t0=t0,
    )

    add_synced, remaining = run_retry_passes(
        failed_ids,
        workers=workers,
        attempts=UPSERT_ATTEMPTS,
        rounds=SECOND_PASSES,
        progress=progress,
        logger=logger,
        t0=t0,
    )

    elapsed = round(time.perf_counter() - t0, 2)
    return {
        "synced": synced + add_synced,
        "skipped": skipped,
        "failed": len(remaining),
        "total": total,
        "elapsed": elapsed,
    }