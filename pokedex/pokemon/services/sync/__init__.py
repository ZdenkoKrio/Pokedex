from __future__ import annotations
"""
sync package

Unified namespace that bundles all sync subpackages:

- core : generic reusable building blocks
- pokemon   : Pokémon-specific bulk sync and upsert
- evo  : Evolution-chain-specific bulk sync and upsert
"""

from . import core
from . import pokemon
from . import evo

