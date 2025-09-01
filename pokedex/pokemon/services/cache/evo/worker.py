from __future__ import annotations
"""
ThreadPool worker for evolution-chains.
Builds a safe runner for upserts with retry + backoff.
"""

from concurrent.futures import ThreadPoolExecutor
from typing import Sequence
from ..core.worker import make_safe_runner, submit_chunk as _submit
from ..core.constants import LogFn
from .upsert import upsert_evo_chain


ATTEMPTS_DEFAULT = 4


def submit_chunk(ex: ThreadPoolExecutor, ids: Sequence[int], *, logger: LogFn):
    runner = make_safe_runner(upsert_evo_chain, attempts=ATTEMPTS_DEFAULT, logger=logger)
    return _submit(ex, ids, runner=runner)