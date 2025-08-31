from __future__ import annotations
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST

from .session import get_session_list, save_session_list


@require_POST
def compare_toggle(request: HttpRequest, pokeapi_id: int) -> JsonResponse:
    """
    Toggle Pokémon ID in the session-based compare list.
    - If present → remove.
    - If absent  → add.
    Returns JSON with current state (ok, action, count, ids).
    """
    ids = get_session_list(request)

    if pokeapi_id in ids:
        ids = [i for i in ids if i != pokeapi_id]
        action = "removed"
    else:
        ids.append(pokeapi_id)
        action = "added"

    save_session_list(request, ids)
    return JsonResponse({"ok": True, "action": action, "count": len(ids), "ids": ids})