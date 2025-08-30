from __future__ import annotations
"""
Pure helpers for shaping PokeAPI payloads.

These functions have NO Django/DB dependencies.
"""

from typing import Dict, Iterable, List, Tuple
from pokemon.services.api import get_json


def stat_dict(stats: Iterable[dict]) -> Dict[str, int]:
    """Map `stats` array to a flat dict, e.g. {'hp': 45, 'attack': 49, ...}."""
    out: Dict[str, int] = {}
    for s in stats or []:
        name = (s.get("stat") or {}).get("name")
        val = s.get("base_stat")
        if name is not None and val is not None:
            out[name] = int(val)
    return out


def taxonomy_slugs_from_payload(d: dict) -> Tuple[List[str], List[str]]:
    """
    Extract type and ability slugs from `/pokemon/<id-or-name>` payload.

    Returns
    -------
    (type_slugs, ability_slugs)
    """
    types: List[str] = []
    for t in (d.get("types") or []):
        slug = (t.get("type") or {}).get("name")
        if slug:
            types.append(slug)

    abilities: List[str] = []
    for a in (d.get("abilities") or []):
        slug = (a.get("ability") or {}).get("name")
        if slug:
            abilities.append(slug)

    return types, abilities


def species_payload_for(pokemon_payload: dict) -> dict:
    """
    Fetch `/pokemon-species/<id>/` for generation/is_legendary/is_mythical.

    Network: yes (but cached through services.api).
    """
    species_url = (pokemon_payload.get("species") or {}).get("url")
    return get_json(species_url) if species_url else {}