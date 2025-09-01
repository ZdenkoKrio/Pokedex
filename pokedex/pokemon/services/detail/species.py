from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
from pokemon.services.api import get_json, url

GENERATION_TO_REGION = {
    "generation-i": "Kanto",
    "generation-ii": "Johto",
    "generation-iii": "Hoenn",
    "generation-iv": "Sinnoh",
    "generation-v": "Unova",
    "generation-vi": "Kalos",
    "generation-vii": "Alola",
    "generation-viii": "Galar",
    "generation-ix": "Paldea",
}


def fetch_species(pokeapi_id: int) -> Dict[str, Any]:
    """Fetch and cache /pokemon-species/{id}/ payload."""
    return get_json(url("pokemon-species", pokeapi_id))


def pick_english_text(entries: List[Dict[str, Any]], key: str) -> Optional[str]:
    """
    Extract the newest available English text for the given key (e.g. 'genus', 'flavor_text').
    """
    for e in sorted(entries, key=lambda r: (r.get("version") or {}).get("name", ""), reverse=True):
        lang = (e.get("language") or {}).get("name")
        txt = e.get(key)
        if lang == "en" and txt:
            return txt.replace("\n", " ").replace("\f", " ").strip()

    for e in entries:
        if (e.get("language") or {}).get("name") == "en" and e.get(key):
            return e[key].replace("\n", " ").replace("\f", " ").strip()

    return None


def normalize_species(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Curate species payload for template use.
    Returns dict with genus, flavor_text, egg_groups, growth_rate, color, shape, habitat,
    capture_rate, base_happiness, gender_rate, generation, region, varieties.
    """
    genera = pick_english_text(spec.get("genera", []), "genus") or ""
    flavor = pick_english_text(spec.get("flavor_text_entries", []), "flavor_text")
    egg_groups = [g["name"] for g in spec.get("egg_groups", []) if g and "name" in g]
    growth_rate = (spec.get("growth_rate") or {}).get("name")
    color = (spec.get("color") or {}).get("name")
    shape = (spec.get("shape") or {}).get("name")
    habitat = (spec.get("habitat") or {}).get("name")
    capture_rate = spec.get("capture_rate")
    base_happiness = spec.get("base_happiness")
    gender_rate = spec.get("gender_rate")  # -1 = genderless; otherwise 0..8 (♀ share = rate/8)

    generation_slug = (spec.get("generation") or {}).get("name")
    region = GENERATION_TO_REGION.get(generation_slug)

    varieties = [
        {
            "name": v.get("pokemon", {}).get("name"),
            "is_default": v.get("is_default", False),
            "id": int((v.get("pokemon", {}).get("url", " / ").rstrip("/").split("/") or ["0"])[-1]),
        }
        for v in spec.get("varieties", [])
        if v.get("pokemon", {}).get("url")
    ]

    return {
        "genera": genera,
        "flavor_text": flavor,
        "egg_groups": egg_groups,
        "growth_rate": growth_rate,
        "color": color,
        "shape": shape,
        "habitat": habitat,
        "capture_rate": capture_rate,
        "base_happiness": base_happiness,
        "gender_rate": gender_rate,
        "generation": generation_slug,
        "region": region,
        "varieties": varieties,
    }