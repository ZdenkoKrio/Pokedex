from __future__ import annotations
import time
from .constants import ProgressFn


def report(progress: ProgressFn, **state) -> None:
    """Send any shaped progress payload to the callback (caller controls keys)."""
    if progress:
        progress(state)


def compute_metrics(total: int, done: int, t0: float) -> tuple[float, float]:
    """Return (rate items/s, eta seconds)."""
    elapsed = time.perf_counter() - t0
    rate = (done / elapsed) if elapsed > 0 else 0.0
    remaining = max(0, total - done)
    eta = (remaining / rate) if rate > 0 else 0.0
    return rate, eta