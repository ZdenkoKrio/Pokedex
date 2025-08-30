from __future__ import annotations
"""
ProgressPrinter – tiny utility for live CLI progress.

This module provides a minimal, dependency-free way to print a single
live-updating progress line to a TTY (e.g. during long-running syncs).
It also supports one-off lines (e.g. index results) and ensures the
live line is properly finalized with a trailing newline.

Typical usage:
    printer = ProgressPrinter(enabled=True)
    printer.line("[index] discovered ~1302 Pokémon")

    # called repeatedly from a progress callback:
    printer.live({
        "phase": "sync", "total": 200, "done": 37,
        "synced": 35, "failed": 2, "skipped": 0,
        "batch": 1, "batches": 8, "rate": 4.2, "eta": 38,
    })

    # make sure to finalize to drop the cursor to the next line:
    printer.finalize_line()

Notes:
- The expected `state` dictionary keys are optional; missing values are
  rendered with sensible defaults.
- This utility is intentionally simple and NOT thread-safe. Call it from
  a single thread (e.g. your management command process).
- If output is redirected to a file (non-TTY), the live line will still
  be emitted but without carriage-return animation benefits.
"""

import sys
from typing import Dict, Optional, TextIO


class ProgressPrinter:
    """
    Minimal live progress helper for CLI programs.

    Responsibilities:
    - Print one-off messages via `line()`.
    - Render a single live-updating progress row via `live(state)`.
    - Ensure the live row is terminated via `finalize_line()`.

    Parameters
    ----------
    enabled : bool
        If False, all methods become no-ops (useful for `--no-progress`).
    stream : TextIO
        Output stream; defaults to `sys.stdout`.

    Expected `state` keys (all optional)
    ------------------------------------
    phase: str         e.g. "sync", "retry-1", "index"
    total: int         total work units for this phase
    done: int          completed work units
    synced: int        successful items in this phase so far
    failed: int        failed items in this phase so far
    skipped: int       skipped items (e.g., already present)
    batch: int         current batch number (1-based)
    batches: int       total number of batches
    rate: float        items per second
    eta: int|float     estimated seconds remaining
    """

    def __init__(self, enabled: bool = True, stream: Optional[TextIO] = None):
        self.enabled = enabled
        self.stream: TextIO = stream or sys.stdout
        self._live_active = False

    def line(self, text: str) -> None:
        """
        Print a single message followed by a newline.

        Use for non-live events (e.g., post-index summary).
        """
        if not self.enabled:
            return
        self.stream.write(text + "\n")
        self.stream.flush()
        self._live_active = False

    def live(self, state: Dict) -> None:
        """
        Render/update the live progress line.

        The line is re-written in place using a carriage return (`\\r`).
        Call `finalize_line()` once you are done to emit a newline so the
        shell prompt or subsequent prints appear on a new line.
        """
        if not self.enabled:
            return

        phase = state.get("phase", "sync")
        total = max(1, int(state.get("total", 1)))
        done = int(state.get("done", 0))
        percent = min(100, int(done * 100 / total))

        synced = state.get("synced", 0)
        failed = state.get("failed", 0)
        skipped = state.get("skipped", 0)

        batch = state.get("batch", 0)
        batches = state.get("batches", 0)
        rate = float(state.get("rate", 0.0))
        eta = int(state.get("eta", 0.0))

        phase_label = f"{phase} {batch}/{batches}" if batch and batches else phase
        msg = (
            f"\r[{phase_label}] {percent:3d}% | "
            f"done {done}/{total} | ok {synced} | fail {failed} | "
            f"skip {skipped} | {rate:.1f}/s | ETA {eta}s"
        )
        self.stream.write(msg)
        self.stream.flush()
        self._live_active = True

    def finalize_line(self) -> None:
        """
        Ensure the live progress line is terminated with a newline.

        Call this in a `finally:` block or at the end of the run so the
        cursor moves to the next line. Safe to call multiple times.
        """
        if not self.enabled:
            return
        if self._live_active:
            self.stream.write("\n")
            self.stream.flush()
            self._live_active = False