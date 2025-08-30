from __future__ import annotations
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Sequence, Any
from .constants import LogFn


def make_safe_runner(
    upsert_fn: Callable[[Any], Any],  # noqa: ANN401
    *,
    attempts: int,
    logger: LogFn = None,
) -> Callable[[Any], bool]:  # noqa: ANN401
    """
    Build a resilient runner for a single ID:
    - retries with exponential backoff + tiny jitter
    - returns True/False
    - logs first failure and final give-up if logger is provided
    """
    def _log(msg: str) -> None:
        if logger:
            logger(msg)

    def _runner(item_id: Any) -> bool:  # noqa: ANN401
        last_err: Exception | None = None
        for i in range(attempts):
            try:
                upsert_fn(item_id)
                return True

            except Exception as e:  # noqa: BLE001
                last_err = e
                if i == 0:
                    _log(f"[safe-runner] id={item_id} first fail: {e!r}")
                sleep_s = min(4.0, 0.5 * (2 ** i)) + random.uniform(0.0, 0.2)
                time.sleep(sleep_s)

        _log(f"[safe-runner] id={item_id} giving up after {attempts} attempts. last={last_err!r}")
        return False

    return _runner


def submit_chunk(
    ex: ThreadPoolExecutor,
    ids: Sequence[Any],  # noqa: ANN401
    *,
    runner: Callable[[Any], bool],  # noqa: ANN401
):
    """Submit a batch of IDs to the executor using the prepared `runner`."""
    return [ex.submit(runner, item_id) for item_id in ids]