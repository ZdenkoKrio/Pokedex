from __future__ import annotations
from typing import Dict, Tuple


ALLOWED = {"default", "shiny", "animated", "artwork"}


def sprite_bundle(any_id: int, raw_mode: str | None) -> Tuple[str, Dict[str, str]]:
    """
    Build sprite URLs (default, shiny, animated, artwork) for a given Pokémon ID.
    Returns (mode, urls).
    """
    mode = (raw_mode or "default").lower()
    if mode not in ALLOWED:
        mode = "default"

    sid = str(any_id)
    urls = {
        "default":  f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{sid}.png",
        "shiny":    f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{sid}.png",
        "animated": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{sid}.gif",
        "artwork":  f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{sid}.png",
    }
    return mode, urls