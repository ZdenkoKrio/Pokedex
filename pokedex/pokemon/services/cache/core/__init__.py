from __future__ import annotations
"""
sync_core package

Generic, reusable building blocks for bulk syncs
(shared by Pokémon sync and Evolution-chain sync).

Submodules:
- constants : default knobs + type aliases
- dbutils   : generic DB helpers (have/missing values)
- indexing  : generic PokeAPI index iteration
- progress  : progress reporting helpers
- steps     : orchestration steps (enumerate, select_targets, run passes)
- worker    : resilient runner + chunk submitter
"""

from .constants import (
    PAGE_SIZE_DEFAULT,
    MAX_WORKERS_DEFAULT,
    SECOND_PASSES,
    UPSERT_ATTEMPTS,
    PROGRESS_EVERY_N,
    ProgressState,
    ProgressFn,
    LogFn,
)
from .dbutils import db_have_values, missing_after_chunk
from .indexing import extract_ids_from_index, get_total_count, iter_index_ids
from .progress import report, compute_metrics
from .steps import (
    enumerate_ids,
    select_targets,
    run_main_pass,
    run_retry_passes,
)
from .worker import make_safe_runner, submit_chunk

__all__ = [
    # constants
    "PAGE_SIZE_DEFAULT",
    "MAX_WORKERS_DEFAULT",
    "SECOND_PASSES",
    "UPSERT_ATTEMPTS",
    "PROGRESS_EVERY_N",
    "ProgressState",
    "ProgressFn",
    "LogFn",
    # db
    "db_have_values",
    "missing_after_chunk",
    # indexing
    "extract_ids_from_index",
    "get_total_count",
    "iter_index_ids",
    # progress
    "report",
    "compute_metrics",
    # steps
    "enumerate_ids",
    "select_targets",
    "run_main_pass",
    "run_retry_passes",
    # worker
    "make_safe_runner",
    "submit_chunk",
]