from __future__ import annotations
"""
SyncRunner — small orchestrator for multi-pass full Pokédex syncs.

Responsibilities
- Call `sync_all_pokemon` repeatedly.
- Tweak params between runs (fewer workers, more sleep).
- Stop early when failures drop under a target.
- Aggregate simple totals across runs.

No hard dependency on Django; an optional `logger` (e.g. `self.stdout`)
may be provided for messages and warnings.
"""

import time
from typing import Optional, Dict, Callable, Tuple, Protocol
from pokemon.services.sync_all import sync_all_pokemon


class _LoggerLike(Protocol):
    """Minimal interface accepted as `logger`."""
    def write(self, s: str) -> object: ...
    def info(self, s: str) -> object: ...
    def warning(self, s: str) -> object: ...
    def error(self, s: str) -> object: ...


class SyncRunner:
    """
    Run multiple sync passes until failures are low enough.

    Each pass delegates to `sync_all_pokemon`, optionally reporting progress
    via a callback. Between passes, workers are reduced slightly and a small
    delay is added to ease transient API failures.

    Parameters
    ----------
    workers : int
        Initial parallel worker count for HTTP work.
    batch_size : int
        Index page size used to enumerate IDs.
    base_sleep : float
        Base inter-batch sleep per run (seconds).
    refresh_all : bool
        If True, refresh also existing records; otherwise fetch only missing.
    max_runs : int
        Upper bound on how many passes to attempt.
    target_fail : int
        Stop early once `failed <= target_fail`.
    progress : Callable[[dict], None] | None
        Optional callback receiving progress dicts from the service.
    logger : _LoggerLike | None
        Optional sink for log lines (supports `.write()` or `.warning()`, etc.).

    Results (from `run()`)
    ----------------------
    dict with keys:
      runs, total_synced, total_skipped, last_failed
    """

    def __init__(
        self,
        workers: int,
        batch_size: int,
        base_sleep: float,
        refresh_all: bool,
        max_runs: int,
        target_fail: int,
        progress: Optional[Callable[[Dict], None]] = None,
        logger: Optional[_LoggerLike] = None,
    ):
        self.base_workers = workers
        self.batch_size = batch_size
        self.base_sleep = base_sleep
        self.refresh_all = refresh_all
        self.max_runs = max(1, max_runs)
        self.target_fail = max(0, target_fail)
        self.progress = progress
        self.log = logger

        self.total_synced = 0
        self.total_skipped = 0
        self.last_failed: Optional[int] = None

    def _adaptive_params(self, run_index: int) -> Tuple[int, float]:
        """
        Compute run-specific params.

        Strategy:
        - Slightly decrease workers over time (≈ every two runs).
        - Slightly increase sleep every run.

        `run_index` is 1-based.
        """
        workers = max(1, self.base_workers - (run_index - 1) // 2)
        sleep_between = self.base_sleep + 0.1 * (run_index - 1)
        return workers, sleep_between

    def _log(self, text: str, level: str = "info") -> None:
        """Emit a log line if `logger` is present."""
        if not self.log:
            return

        if hasattr(self.log, "write"):            # e.g. Django's self.stdout
            self.log.write(text + "\n")

        elif hasattr(self.log, level):            # e.g. logger.warning(...)
            getattr(self.log, level)(text)

    def run(self) -> Dict:
        """
        Execute up to `max_runs` passes with adaptive throttling.

        Loop:
          1) call `sync_all_pokemon` with current params
          2) aggregate totals
          3) stop if failures are under target; otherwise short sleep

        Returns
        -------
        dict: {"runs", "total_synced", "total_skipped", "last_failed"}
        """
        for run in range(1, self.max_runs + 1):
            workers, sleep_between = self._adaptive_params(run)
            self._log(
                f"Run {run}/{self.max_runs} — workers={workers}, batch-size={self.batch_size}, "
                f"sleep={sleep_between:.1f}, refresh_all={self.refresh_all}"
            )

            stats = sync_all_pokemon(
                workers=workers,
                batch_size=self.batch_size,
                sleep_between_batches=sleep_between,
                only_missing=not self.refresh_all,
                progress=self.progress,
                # Forward taxonomy warnings (missing type/ability/generation) as warnings:
                logger=(lambda s: self._log(s, "warning")),
            )

            # Aggregate per-run numbers
            self.total_synced += int(stats.get("synced", 0))
            self.total_skipped += int(stats.get("skipped", 0))
            self.last_failed = int(stats.get("failed", 0))

            # Per-run summary
            self._log(
                f"[run {run}] total={stats.get('total', 0)} "
                f"synced={stats.get('synced', 0)} skipped={stats.get('skipped', 0)} "
                f"failed={stats.get('failed', 0)} elapsed={stats.get('elapsed', 0.0)}s"
            )

            if self.last_failed <= self.target_fail:
                break

            # Short pause before the next pass to ease public API pressure.
            time.sleep(1.0 + 0.5 * run)

        return {
            "runs": run,
            "total_synced": self.total_synced,
            "total_skipped": self.total_skipped,
            "last_failed": self.last_failed,
        }