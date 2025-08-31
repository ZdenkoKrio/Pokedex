from __future__ import annotations
from typing import Dict


SESSION_KEY = "compare_ids"


def compare_context(request) -> Dict[str, int]:
    ids = request.session.get(SESSION_KEY, [])
    return {"compare_count": len(ids)}