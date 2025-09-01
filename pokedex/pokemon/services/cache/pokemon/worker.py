from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from typing import Sequence

from .upsert import upsert_pokemon_from_api
from ..core.worker import make_safe_runner, submit_chunk as _submit
from ..core.constants import LogFn


def submit_chunk(
    ex: ThreadPoolExecutor,
    ids: Sequence[int],
    *,
    attempts: int,
    logger: LogFn,
):
    """
    Prepare a resilient runner (retries + backoff) for the Pokémon upsert
    and submit a chunk of IDs to the executor.
    """
    runner = make_safe_runner(upsert_pokemon_from_api, attempts=attempts, logger=logger)
    return _submit(ex, ids, runner=runner)