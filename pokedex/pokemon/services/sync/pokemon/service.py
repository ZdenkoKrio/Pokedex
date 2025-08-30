from __future__ import annotations
"""
Bulk Pokédex sync orchestrator built from shared generic steps.
"""

import time
from ..core.steps import (
    enumerate_ids as core_enumerate_ids,
    select_targets as core_select_targets,
    run_main_pass as core_run_main_pass,
    run_retry_passes as core_run_retry_passes,
)
from ..core.constants import (
    PAGE_SIZE_DEFAULT,
    MAX_WORKERS_DEFAULT,
    SECOND_PASSES,
    UPSERT_ATTEMPTS,
    PROGRESS_EVERY_N,
    ProgressFn,
    LogFn,
)

from .indexing import iter_index_ids
from .dbutils import db_have_ids, missing_after_chunk
from .worker import submit_chunk


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
    Fetch/refresh ALL Pokémon into the local DB cache.
    Taxonomies are not created here; upsert links to what already exists.
    """
    # 1) enumerate IDs (generic)
    all_ids, t0 = core_enumerate_ids(iter_index_ids, batch_size, progress)
    total = len(all_ids)
    if total == 0:
        return {"synced": 0, "skipped": 0, "failed": 0, "total": 0, "elapsed": 0.0}

    # 2) choose targets (generic)
    existing = db_have_ids(all_ids)
    targets, skipped = core_select_targets(all_ids, existing, only_missing)
    if not targets:
        elapsed = round(time.perf_counter() - t0, 2)
        return {"synced": 0, "skipped": skipped, "failed": 0, "total": total, "elapsed": elapsed}

    # 3) main pass (generic runner + Pokémon worker/missing fns)
    synced, failed_ids, _ = core_run_main_pass(
        targets,
        workers=workers,
        batch_size=batch_size,
        sleep_between_batches=sleep_between_batches,
        submit_chunk=lambda ex, chunk: submit_chunk(ex, chunk, attempts=UPSERT_ATTEMPTS, logger=logger),
        progress=progress,
        metric_key="synced",
        progress_every_n=PROGRESS_EVERY_N,
        missing_after_chunk=missing_after_chunk,
        t0=t0,
    )

    # 4) retry passes (generic)
    add_synced, remaining = core_run_retry_passes(
        failed_ids,
        workers=workers,
        rounds=SECOND_PASSES,
        submit_chunk_retry=lambda ex, ids: submit_chunk(
            ex, ids, attempts=max(1, UPSERT_ATTEMPTS // 2), logger=logger
        ),
        have_in_db=db_have_ids,
        progress=progress,
        metric_key="synced",
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