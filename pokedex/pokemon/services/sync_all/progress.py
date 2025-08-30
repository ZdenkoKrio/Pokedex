from __future__ import annotations
"""
Progress reporting helper.
"""

import time
from .constants import ProgressFn


def report_progress(
    progress: ProgressFn,
    phase: str,
    total: int,
    done: int,
    synced: int,
    failed_count: int,
    skipped: int,
    batch: int,
    batches: int,
    t0: float,
) -> None:
    """Send a uniform progress payload to the callback."""
    if not progress:
        return

    elapsed = time.perf_counter() - t0
    rate = (done / elapsed) if elapsed > 0 else 0.0
    remaining = max(0, total - done)
    eta = (remaining / rate) if rate > 0 else 0.0
    progress({
        "phase": phase,
        "total": total,
        "done": done,
        "synced": synced,
        "failed": failed_count,
        "skipped": skipped,
        "batch": batch,
        "batches": batches,
        "rate": rate,
        "eta": eta,
    })