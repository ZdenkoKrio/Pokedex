from __future__ import annotations
from typing import Dict, List, Tuple, Optional

from .types import JSON, Group, MoveItem
from .constants import LEARN_ORDER
from .iterators import available_vgs, pick_active_vg, iter_moves


def extract_pokemon_moves(
    pokemon_payload: JSON,
    *,
    version_group: Optional[str] = None,
) -> Tuple[List[Group], List[str], str]:
    """
    Returns:
      - grouped: [{ "key": method, "items": [MoveItem, ...] }]
      - available_vgs: list[str]
      - active_vg: str ("" if none)
    """
    avgs = available_vgs(pokemon_payload)
    active = pick_active_vg(pokemon_payload, version_group)

    buckets: Dict[str, Dict[int, MoveItem]] = {k: {} for k in LEARN_ORDER}

    for mv_id, mv_name, method, level in iter_moves(pokemon_payload, active):
        if method not in buckets:
            continue

        cur = buckets[method].get(mv_id)
        if cur is None:
            buckets[method][mv_id] = {"id": mv_id, "name": mv_name, "level": level, "url": None}

        elif method == "level-up":
            cur_lvl = int(cur.get("level") or 0)
            if 0 < level < (cur_lvl or 10**9):
                cur["level"] = level

    groups: List[Group] = []
    for method in LEARN_ORDER:
        items = list(buckets[method].values())
        if method == "level-up":
            items.sort(key=lambda m: (m.get("level", 0), m.get("name", "")))

        else:
            items.sort(key=lambda m: m.get("name", ""))
        groups.append({"key": method, "items": items})

    return groups, avgs, (active or "")