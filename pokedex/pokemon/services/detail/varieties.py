from __future__ import annotations
from typing import Dict, Any, List


def build_varieties_strip(species_normalized: Dict[str, Any], current_any_id: int) -> List[Dict[str, Any]]:
    """
    Prepare variety/form list for UI.
    Returns [{id, name, is_default, sprite, active}, ...].
    """
    out: List[Dict[str, Any]] = []
    for v in species_normalized.get("varieties") or []:
        vid = int(v.get("id") or 0)
        if not vid:
            continue

        out.append({
            "id": vid,
            "name": (v.get("name") or "").replace("-", " "),
            "is_default": bool(v.get("is_default")),
            "sprite": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{vid}.png",
            "active": (vid == current_any_id),
        })

    return out