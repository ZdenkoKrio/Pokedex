from __future__ import annotations
"""
Pure extractor for species IDs from an evolution-chain payload.
No Django/DB dependencies.
"""

from typing import List


def species_ids_from_raw(evo_raw: dict) -> List[int]:
    """
    Extract species IDs in a stable DFS order from an /evolution-chain payload.

    Expected shape:
      evo_raw["chain"] -> node with keys:
        - "species" (url)
        - "evolves_to" (list of nodes)
    """
    out: List[int] = []

    def walk(node: dict) -> None:
        sid = int(node["species"]["url"].rstrip("/").split("/")[-1])  # /pokemon-species/<id>/
        out.append(sid)
        for nxt in node.get("evolves_to") or []:
            walk(nxt)

    walk(evo_raw["chain"])
    return out