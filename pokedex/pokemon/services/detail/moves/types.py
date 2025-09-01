from __future__ import annotations
from typing import Any, Dict, Callable


JSON = Dict[str, Any]
MoveRow = Dict[str, Any]
MoveItem = Dict[str, Any]
Group = Dict[str, Any]

FetchMoveFn = Callable[[int], JSON]