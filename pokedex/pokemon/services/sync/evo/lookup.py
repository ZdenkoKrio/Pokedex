from __future__ import annotations
"""
Helpers to resolve and ensure EvolutionChainCache for a given species/pokédex id.
"""

from typing import Optional

from pokemon.models import EvolutionChainCache
from pokemon.services.api import get_json, url
from .upsert import upsert_evo_chain


def _chain_id_from_species_payload(species: dict) -> Optional[int]:
    chain_url = (species.get("evolution_chain") or {}).get("url")
    if not chain_url:
        return None
    try:
        return int(str(chain_url).rstrip("/").split("/")[-1])

    except Exception:
        return None


def ensure_chain_for_species(species_id: int) -> Optional[int]:
    """
    Ensure the evolution chain for `species_id` exists in EvolutionChainCache.
    Returns the chain_id (or None if not available).

    Logic:
    - read species payload (/pokemon-species/<id>/)
    - parse evolution_chain.id
    - if not cached, upsert_evo_chain(chain_id)
    """
    species = get_json(url("pokemon-species", species_id))
    if not species:
        return None

    chain_id = _chain_id_from_species_payload(species)
    if not chain_id:
        return None

    exists = EvolutionChainCache.objects.filter(chain_id=chain_id).only("id").exists()
    if not exists:
        upsert_evo_chain(chain_id)

    return chain_id