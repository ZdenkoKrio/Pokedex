from __future__ import annotations
"""
Bulk evolution-chain sync orchestrator composed from shared generic steps.

- Enumerates /evolution-chain IDs.
- Upserts chains in parallel (retry/backoff is handled in the worker).
- Backfills PokemonCache.evolution_chain_id inside the upsert layer.
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
    ProgressFn,
    LogFn,
)
from .indexing import iter_chain_ids
from .dbutils import db_have_chain_ids, missing_after_chunk
from .worker import submit_chunk


PROGRESS_EVERY_N = 5


def sync_all_evo_chains(
    workers: int = MAX_WORKERS_DEFAULT,
    batch_size: int = PAGE_SIZE_DEFAULT,
    sleep_between_batches: float = 0.0,
    only_missing: bool = True,
    progress: ProgressFn = None,
    *,
    logger: LogFn = None,
) -> dict:
    """
    Fetch/refresh all evolution chains into EvolutionChainCache.

    Returns
    -------
    dict: {"ok", "skipped", "failed", "total", "elapsed"}
    """
    all_ids, t0 = core_enumerate_ids(iter_chain_ids, batch_size, progress)
    total = len(all_ids)
    if total == 0:
        return {"ok": 0, "skipped": 0, "failed": 0, "total": 0, "elapsed": 0.0}

    existing = db_have_chain_ids(all_ids)
    targets, skipped = core_select_targets(all_ids, existing, only_missing)
    if not targets:
        elapsed = round(time.perf_counter() - t0, 2)
        return {"ok": 0, "skipped": skipped, "failed": 0, "total": total, "elapsed": elapsed}

    ok, failed_ids, _ = core_run_main_pass(
        targets,
        workers=workers,
        batch_size=batch_size,
        sleep_between_batches=sleep_between_batches,
        submit_chunk=lambda ex, chunk: submit_chunk(ex, chunk, logger=logger),
        progress=progress,
        metric_key="ok",
        progress_every_n=PROGRESS_EVERY_N,
        missing_after_chunk=missing_after_chunk,
        t0=t0,
    )

    add_ok, remaining = core_run_retry_passes(
        failed_ids,
        workers=workers,
        rounds=SECOND_PASSES,
        submit_chunk_retry=lambda ex, ids: submit_chunk(ex, ids, logger=logger),
        have_in_db=db_have_chain_ids,
        progress=progress,
        metric_key="ok",
        t0=t0,
    )

    elapsed = round(time.perf_counter() - t0, 2)
    return {
        "ok": ok + add_ok,
        "skipped": skipped,
        "failed": len(remaining),
        "total": total,
        "elapsed": elapsed,
    }