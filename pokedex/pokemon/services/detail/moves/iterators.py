from __future__ import annotations
from typing import Iterable, Optional, Tuple, List

from .types import JSON
from .constants import VG_INDEX


def available_vgs(payload: JSON) -> List[str]:
    """All version groups present in payload, ordered by VG_ORDER index."""
    vgs: set[str] = set()
    for row in payload.get("moves", []):
        for vd in row.get("version_group_details", []):
            name = (vd.get("version_group") or {}).get("name")
            if name:
                vgs.add(name)

    return sorted(vgs, key=lambda n: VG_INDEX.get(n, -1))


def pick_active_vg(payload: JSON, requested: Optional[str]) -> Optional[str]:
    """Requested VG or the newest present in payload."""
    if requested:
        return requested

    vgs = available_vgs(payload)
    if not vgs:
        return None

    return max(vgs, key=lambda n: VG_INDEX.get(n, -1))


def iter_moves(payload: JSON, active_vg: Optional[str]) -> Iterable[Tuple[int, str, str, int]]:
    """
    Yield (move_id, move_name, method, level) filtered by active_vg.
    """
    for row in payload.get("moves", []):
        mv = row.get("move") or {}
        mv_name = mv.get("name")
        mv_url = mv.get("url")
        if not (mv_name and mv_url):
            continue
        try:
            mv_id = int(str(mv_url).rstrip("/").split("/")[-1])
        except Exception:
            continue

        for vd in row.get("version_group_details", []):
            vg = (vd.get("version_group") or {}).get("name")
            if active_vg and vg != active_vg:
                continue

            method = (vd.get("move_learn_method") or {}).get("name")
            level = int(vd.get("level_learned_at") or 0)
            yield (mv_id, mv_name, method, level)