from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from favorites.selectors import user_favorite_ids
from pokemon.models import PokemonCache


class OwnerRequiredMixin(UserPassesTestMixin):
    """Restrict access: only the team owner can perform this action."""
    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_authenticated and obj.owner_id == self.request.user.id

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(self.request.get_full_path())
        raise Http404("Team not found.")


class TeamPickHelpersMixin:
    """
    Add helper lists to the template context:

    - `fav_options`: list of user's favorite Pokémon [{'id': 25, 'name': 'pikachu'}, ...].
    - `pokemon_index`: index of all Pokémon (id + name) for <datalist> search.
    """

    def _inject_pick_helpers(self, ctx: dict) -> None:
        fav_ids = user_favorite_ids(self.request.user)
        fav_qs = PokemonCache.objects.filter(pokeapi_id__in=fav_ids).only("pokeapi_id", "name")
        ctx["fav_options"] = [{"id": p.pokeapi_id, "name": p.name} for p in fav_qs]

        all_qs = PokemonCache.objects.only("pokeapi_id", "name").order_by("pokeapi_id")
        ctx["pokemon_index"] = [{"id": p.pokeapi_id, "name": p.name} for p in all_qs]