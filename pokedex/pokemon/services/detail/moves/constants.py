from __future__ import annotations
from typing import List, Tuple


VG_ORDER: List[str] = [
    "red-blue", "yellow", "gold-silver", "crystal",
    "ruby-sapphire", "emerald", "firered-leafgreen",
    "diamond-pearl", "platinum", "heartgold-soulsilver",
    "black-white", "black-2-white-2",
    "x-y", "omega-ruby-alpha-sapphire",
    "sun-moon", "ultra-sun-ultra-moon", "lets-go-pikachu-lets-go-eevee",
    "sword-shield", "brilliant-diamond-and-shining-pearl",
    "legends-arceus", "scarlet-violet",
]
VG_INDEX = {name: i for i, name in enumerate(VG_ORDER)}

LEARN_ORDER: Tuple[str, ...] = ("level-up", "machine", "tutor", "egg")