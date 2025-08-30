from __future__ import annotations
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Sequence

from pokemon.services.pokemon_sync import upsert_pokemon_from_api
from .constants import LogFn


def safe_upsert(pid: int, attempts: int, *, logger: LogFn) -> bool:
    """
    Retry a single Pokémon upsert with exponential backoff.
    """
    for i in range(attempts):
        try:
            upsert_pokemon_from_api(pid)
            return True
        except Exception:
            # Exponential backoff with small jitter
            sleep_s = min(4.0, 0.5 * (2 ** i)) + random.uniform(0.0, 0.2)
            time.sleep(sleep_s)
    return False


def submit_chunk(ex: ThreadPoolExecutor, ids: Sequence[int], *, attempts: int, logger: LogFn):
    """Submit a batch of IDs to the executor and return their futures."""
    return [ex.submit(safe_upsert, pid, attempts, logger=logger) for pid in ids]