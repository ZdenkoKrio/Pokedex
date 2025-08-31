from __future__ import annotations
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from favorites.selectors import user_favorites_qs
from pokemon.utils.sprites import sprite_url_for_id


class MyFavoritesView(LoginRequiredMixin, TemplateView):
    """
    Read-only page listing the current user's favorites.
    Renders a simple view-model for the template (id, name, sprite, types).
    """
    template_name = "mine.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = user_favorites_qs(self.request.user).order_by("pokeapi_id")

        items = [{
            "id": p.pokeapi_id,
            "name": p.name,
            "sprite": sprite_url_for_id(p.pokeapi_id, "default"),
            "types": [t.slug for t in p.types.all()],
        } for p in qs]

        ctx["items"] = items
        return ctx