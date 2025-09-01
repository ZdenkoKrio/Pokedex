from __future__ import annotations
from typing import Iterable, Dict, List
from pokemon.models import PokemonCache


def build_members_preview(teams: Iterable) -> None:
    """
    Attach a preview of up to 6 Pokémon to each Team.
    Adds `members_preview` as a list of dicts with:
      - id: PokeAPI ID
      - name: Pokémon name (if cached)
      - sprite: default sprite URL
    """
    teams = list(teams)
    if not teams:
        return

    ids = set()
    for t in teams:
        ids.update(t.members.values_list("pokemon_id", flat=True))

    id_to_name: Dict[int, str] = dict(
        PokemonCache.objects
        .filter(pokeapi_id__in=ids)
        .values_list("pokeapi_id", "name")
    )

    for t in teams:
        preview: List[dict] = []
        for m in t.members.all()[:6]:
            pid = m.pokemon_id
            preview.append({
                "id": pid,
                "name": id_to_name.get(pid),
                "sprite": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pid}.png",
            })
        t.members_preview = preview