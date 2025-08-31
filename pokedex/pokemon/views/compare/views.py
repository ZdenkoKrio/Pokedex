from __future__ import annotations
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from pokemon.models import PokemonCache
from pokemon.utils.sprites import sprite_url_for_id
from .session import get_session_list, save_session_list


class CompareView(TemplateView):
    """
    Renders the comparison page with selected Pokémon.

    Workflow:
      1. Loads IDs from session (or from ?ids=... querystring).
      2. Fetches Pokémon from DB in the same order as selected.
      3. Collects stat keys (preferred order first).
      4. Builds view-model (id, name, sprite, stats, etc.).
      5. Renders template with items + stats_keys.
    """
    template_name = "compare.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        ids = get_session_list(request)

        ids_qs = request.GET.get("ids")
        if ids_qs:
            try:
                ids = [int(x) for x in ids_qs.split(",") if x.strip().isdigit()]
                save_session_list(request, ids)
                return redirect(reverse("pokemon:compare"))
            except Exception:
                pass

        if not ids:
            return render(request, self.template_name, {"items": [], "stats_keys": []})

        rows = (
            PokemonCache.objects.filter(pokeapi_id__in=ids)
            .prefetch_related("types")
            .in_bulk(field_name="pokeapi_id")
        )
        items = [rows[i] for i in ids if i in rows]

        keys = set()
        for p in items:
            keys.update((p.base_stats or {}).keys())
        stats_keys = sorted(keys)

        view = []
        for p in items:
            view.append({
                "id": p.pokeapi_id,
                "name": p.name,
                "sprite": sprite_url_for_id(p.pokeapi_id, "default"),
                "types": [t.slug for t in p.types.all()],
                "weight": p.weight,
                "height": p.height,
                "stats": {k: int((p.base_stats or {}).get(k, 0)) for k in stats_keys},
            })

        ctx = {"items": view, "stats_keys": stats_keys}
        return render(request, self.template_name, ctx)