from __future__ import annotations
from typing import Any, Dict, List
from pokemon.services.api import get_json, url


def fetch_encounters(pokeapi_id: int) -> List[Dict[str, Any]]:
    """
    Fetch and normalize Pokémon encounter data.
    Returns a list of {location_area, versions:[{version, max_chance}, ...]}.
    """
    data = get_json(url("pokemon", pokeapi_id) + "encounters")
    out: List[Dict[str, Any]] = []
    for row in data or []:
        loc_name = (row.get("location_area") or {}).get("name")
        details = row.get("version_details", [])
        versions = []

        for d in details:
            ver = (d.get("version") or {}).get("name")
            max_chance = d.get("max_chance")
            versions.append({"version": ver, "max_chance": max_chance})

        if loc_name:
            out.append({"location_area": loc_name, "versions": versions})

    return out