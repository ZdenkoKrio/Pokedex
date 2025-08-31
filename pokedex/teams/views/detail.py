from django.views.generic import DetailView
from django.db import models
from teams.models import Team
from pokemon.models import PokemonCache
from pokemon.utils.sprites import sprite_url_for_id


class TeamDetailView(DetailView):
    """Show team detail with members and stats overview."""
    model = Team
    template_name = "teams/detail.html"
    context_object_name = "team"

    def get_queryset(self):
        qs = Team.objects.prefetch_related("members")
        if self.request.user.is_authenticated:
            return qs.filter(models.Q(is_public=True) | models.Q(owner=self.request.user))
        return qs.filter(is_public=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        team: Team = ctx["team"]

        member_ids = list(team.members.values_list("pokemon_id", flat=True))
        db_pokemon = (
            PokemonCache.objects
            .filter(pokeapi_id__in=member_ids)
            .prefetch_related("types")
        )
        by_id = {p.pokeapi_id: p for p in db_pokemon}

        members_view, discovered_keys = [], set()
        for tm in team.members.all().order_by("slot"):
            p = by_id.get(tm.pokemon_id)
            if not p:
                continue
            base_stats = p.base_stats or {}
            discovered_keys.update(base_stats.keys())
            members_view.append({
                "id": p.pokeapi_id,
                "name": p.name,
                "sprite": sprite_url_for_id(p.pokeapi_id, "default"),
                "stats": {k: int(base_stats.get(k, 0) or 0) for k in base_stats.keys()},
            })

        preferred = ("hp", "attack", "defense", "special-attack", "special-defense", "speed")
        stats_keys = [k for k in preferred if k in discovered_keys] + sorted(
            k for k in discovered_keys if k not in preferred
        )

        ctx["members"] = members_view
        ctx["stats_keys"] = stats_keys
        return ctx