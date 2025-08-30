from __future__ import annotations
"""
Evolution-chain upsert helpers.

- upsert_evo_chain(chain_id): fetch /evolution-chain/<id>/, extract species IDs,
  upsert EvolutionChainCache and (optionally) backfill PokemonCache.evolution_chain_id.
- safe_upsert_evo_chain(...): resilient wrapper with retries, backoff and logging.
"""

import random
import time
from typing import Callable, List, Optional

from django.db import transaction
from pokemon.models import EvolutionChainCache, PokemonCache
from pokemon.services.api import get_json, url
from .evo_chain_ids import species_ids_from_raw

LogFn = Optional[Callable[[str], None]]


def _log(logger: LogFn, msg: str) -> None:
    if logger:
        logger(msg)


def _model_has_field(model, name: str) -> bool:
    return any(getattr(f, "name", "") == name for f in model._meta.get_fields())


@transaction.atomic
def upsert_evo_chain(chain_id: int) -> None:
    evo_raw = get_json(url("evolution-chain", chain_id))
    if not evo_raw or "chain" not in evo_raw:
        raise ValueError(f"Malformed evolution-chain payload for id={chain_id}")

    species_ids: List[int] = species_ids_from_raw(evo_raw)
    if not species_ids:
        raise ValueError(f"No species_ids extracted for chain id={chain_id}")

    EvolutionChainCache.objects.update_or_create(
        chain_id=chain_id,
        defaults={"species_ids": species_ids, "root_species_id": species_ids[0]},
    )

    if _model_has_field(PokemonCache, "evolution_chain_id"):
        present = list(
            PokemonCache.objects
            .filter(pokeapi_id__in=species_ids)
            .only("id", "pokeapi_id", "evolution_chain_id")
        )
        to_update: List[PokemonCache] = []
        for p in present:
            if p.evolution_chain_id != chain_id:
                p.evolution_chain_id = chain_id
                to_update.append(p)

        if to_update:
            PokemonCache.objects.bulk_update(to_update, ["evolution_chain_id"], batch_size=500)


def safe_upsert_evo_chain(
    chain_id: int,
    attempts: int = 4,
    *,
    logger: LogFn = None,
) -> bool:
    last_err: Optional[Exception] = None
    for i in range(attempts):
        try:
            upsert_evo_chain(chain_id)
            return True

        except Exception as e:
            last_err = e
            if i == 0:
                _log(logger, f"[evo-upsert] chain_id={chain_id} first fail: {e!r}")

            sleep_s = min(4.0, 0.5 * (2 ** i)) + random.uniform(0.0, 0.2)
            time.sleep(sleep_s)

    _log(logger, f"[evo-upsert] chain_id={chain_id} giving up after {attempts} attempts. last={last_err!r}")
    return False