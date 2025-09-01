from __future__ import annotations
from typing import Dict, Any, List
import re

FLAVOR_ORDER = [
    "red","blue","yellow",
    "gold","silver","crystal",
    "ruby","sapphire","emerald","firered","leafgreen",
    "diamond","pearl","platinum","heartgold","soulsilver",
    "black","white","black-2","white-2",
    "x","y","omega-ruby","alpha-sapphire",
    "sun","moon","ultra-sun","ultra-moon",
    "lets-go-pikachu","lets-go-eevee",
    "sword","shield",
    "brilliant-diamond","shining-pearl",
    "legends-arceus",
    "scarlet","violet",
]
_FLAVOR_IDX = {n: i for i, n in enumerate(FLAVOR_ORDER)}


def _clean(txt: str) -> str:
    """Remove newlines/whitespace artifacts from raw PokéAPI flavor text."""
    s = re.sub(r"[\n\f\r]+", " ", txt or "").strip()
    return re.sub(r"\s{2,}", " ", s)


def flavor_bundle(species_raw: Dict[str, Any], requested_version: str | None) -> Dict[str, Any]:
    """
    Extract up to 8 unique English flavor texts from /pokemon-species/.
    Returns {"entries": [{version,text}, ...], "active": selected_version}.
    """
    out: List[Dict[str, str]] = []
    seen: set[str] = set()

    for row in species_raw.get("flavor_text_entries") or []:
        if (row.get("language") or {}).get("name") != "en":
            continue

        ver = (row.get("version") or {}).get("name")
        if not ver or ver in seen:
            continue

        text = _clean(row.get("flavor_text") or "")
        if not text:
            continue

        seen.add(ver)
        out.append({"version": ver, "text": text})

    out.sort(key=lambda r: _FLAVOR_IDX.get(r["version"], 10_000))
    out = out[:8]

    req = (requested_version or "").strip().lower()
    active = req if any(e["version"] == req for e in out) else (out[0]["version"] if out else "")

    return {"entries": out, "active": active}