from __future__ import annotations
from functools import lru_cache
from typing import List

from .types import Group, FetchMoveFn, JSON


@lru_cache(maxsize=2048)
def _default_fetch_move(mid: int) -> JSON:
    from pokemon.services.api import get_json, url
    return get_json(url("move", mid))


def annotate_some_moves(
    grouped: List[Group],
    per_group: int = 10,
    *,
    fetch: FetchMoveFn = _default_fetch_move,
) -> List[Group]:
    """
    Annotate first N moves per group with type/power/accuracy/pp/damage_class.
    """
    for g in grouped:
        for i, m in enumerate(g.get("items", ())):
            if i >= per_group:
                break

            try:
                d = fetch(int(m["id"]))
                m.update({
                    "type": (d.get("type") or {}).get("name"),
                    "power": d.get("power"),
                    "accuracy": d.get("accuracy"),
                    "pp": d.get("pp"),
                    "damage_class": (d.get("damage_class") or {}).get("name"),
                })
            except Exception:
                continue

    return grouped