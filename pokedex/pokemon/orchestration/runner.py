from __future__ import annotations
"""
SyncRunner — generic, small orchestrator for multi-pass bulk syncs.

Responsibilities
- Call a provided `run_fn(**kwargs) -> dict` repeatedly (multi-pass).
- Tweak params between runs (fewer workers, slightly more sleep).
- Stop early when failures drop under a target.
- Aggregate simple totals across runs.

Generic knobs
- `run_fn`: the concrete bulk sync function (e.g. `sync_all_pokemon`, `sync_all_evo_chains`)
- `success_key`: which key in the returned stats represents "successful items"
  (e.g. "synced" for Pokémon, "ok" for evo-chains)
- `run_extra_kwargs`: extra kwargs forwarded to `run_fn` on each pass
  (e.g. a `logger` callback)

No hard dependency on Django; you may pass a `logger` (e.g. `self.stdout`) for messages.
"""

import time
from typing import Optional, Dict, Callable, Tuple, Protocol, Any


class _LoggerLike(Protocol):
    """Minimal interface accepted as `logger`."""
    def write(self, s: str) -> object: ...
    def info(self, s: str) -> object: ...
    def warning(self, s: str) -> object: ...
    def error(self, s: str) -> object: ...


class SyncRunner:
    """
    Run multiple sync passes until failures are low enough.

    Each pass calls the injected `run_fn`, optionally reporting progress via a
    callback. Between passes, workers are slightly reduced and a short delay is
    added to help with transient public API issues.

    Parameters
    ----------
    run_fn : Callable[..., dict]
        Bulk sync function; must return a dict with at least keys:
        - 'failed' (int), and a success counter at `success_key`.
    success_key : str
        Name of the success counter in the returned stats (e.g. 'synced', 'ok').
    run_extra_kwargs : dict | None
        Extra kwargs forwarded to `run_fn` on each pass (e.g., {'logger': ...}).

    workers, batch_size, base_sleep, refresh_all, max_runs, target_fail, progress, logger
        Same semantics as before; these are used to build per-pass arguments.
    """

    def __init__(
        self,
        *,
        run_fn: Callable[..., Dict[str, Any]],
        success_key: str,
        run_extra_kwargs: Optional[Dict[str, Any]] = None,

        workers: int,
        batch_size: int,
        base_sleep: float,
        refresh_all: bool,
        max_runs: int,
        target_fail: int,
        progress: Optional[Callable[[Dict], None]] = None,
        logger: Optional[_LoggerLike] = None,
    ):
        self.run_fn = run_fn
        self.success_key = success_key
        self.run_extra_kwargs = dict(run_extra_kwargs or {})

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
        if hasattr(self.log, "write"):            # e.g., Django's self.stdout
            self.log.write(text + "\n")
        elif hasattr(self.log, level):            # e.g., logger.warning(...)
            getattr(self.log, level)(text)

    def run(self) -> Dict[str, Any]:
        """
        Execute up to `max_runs` passes with adaptive throttling.

        Loop:
          1) call `run_fn` with current params
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

            # Build per-pass kwargs for the service
            kwargs = {
                "workers": workers,
                "batch_size": self.batch_size,
                "sleep_between_batches": sleep_between,
                "only_missing": (not self.refresh_all),
                "progress": self.progress,
            }
            kwargs.update(self.run_extra_kwargs)

            stats = self.run_fn(**kwargs)

            # Aggregate per-run numbers
            success = int(stats.get(self.success_key, 0))
            skipped = int(stats.get("skipped", 0))
            failed = int(stats.get("failed", 0))

            self.total_synced += success
            self.total_skipped += skipped
            self.last_failed = failed

            # Per-run summary
            self._log(
                f"[run {run}] total={stats.get('total', 0)} "
                f"{self.success_key}={success} skipped={skipped} "
                f"failed={failed} elapsed={stats.get('elapsed', 0.0)}s"
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