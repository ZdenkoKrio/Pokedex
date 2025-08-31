from __future__ import annotations
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpRequest
from django.views import View

from favorites.models import Favorite


class ToggleFavoriteView(LoginRequiredMixin, View):
    """
    POST /favorites/toggle/<pokeapi_id>/
    Toggles current user's favorite for given PokeAPI id.
    Returns JSON: { ok, action: "added"|"removed", count }
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, pokeapi_id: int, *args, **kwargs) -> JsonResponse:
        obj, created = Favorite.objects.get_or_create(
            user=request.user,
            pokemon_id=pokeapi_id,  # field name in Favorite
        )
        if created:
            action = "added"
        else:
            obj.delete()
            action = "removed"

        count = Favorite.objects.filter(user=request.user).count()
        return JsonResponse({"ok": True, "action": action, "count": count})