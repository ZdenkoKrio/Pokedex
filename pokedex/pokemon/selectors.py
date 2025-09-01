from __future__ import annotations
from typing import List, Dict, Optional
from django.db.models import Q
from pokemon.models import PokemonCache
from pokemon.services.cache.pokemon import upsert_pokemon_from_api

__all__ = ["list_pokemon", "evo_display_from_ids"]


def list_pokemon(
    search: Optional[str] = None,
    type_slug: Optional[str] = None,
    ability_slug: Optional[str] = None,
    min_weight: Optional[int] = None,
    max_weight: Optional[int] = None,
    generation_slug: Optional[str] = None,
    legendary: Optional[bool] = None,
    mythical: Optional[bool] = None,
):
    qs = PokemonCache.objects.prefetch_related("types", "abilities").select_related("generation").all()

    if search:
        s = search.strip()
        cond = Q(name__icontains=s)
        if s.isdigit():
            cond |= Q(pokeapi_id=int(s))
        qs = qs.filter(cond)

    if type_slug:
        qs = qs.filter(types__slug=type_slug)
    if ability_slug:
        qs = qs.filter(abilities__slug=ability_slug)
    if generation_slug:
        qs = qs.filter(generation__slug=generation_slug)

    if legendary is True:
        qs = qs.filter(is_legendary=True)
    elif legendary is False:
        qs = qs.filter(is_legendary=False)

    if mythical is True:
        qs = qs.filter(is_mythical=True)
    elif mythical is False:
        qs = qs.filter(is_mythical=False)

    if min_weight is not None:
        qs = qs.filter(weight__gte=min_weight)
    if max_weight is not None:
        qs = qs.filter(weight__lte=max_weight)

    return qs.distinct()


def _sprite_url(sid: int) -> str:
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{sid}.png"


def evo_display_from_ids(
    species_ids: List[int],
    ensure_missing: bool = False,
) -> List[Dict]:
    if not species_ids:
        return []

    rows = PokemonCache.objects.filter(
        pokeapi_id__in=species_ids
    ).in_bulk(field_name="pokeapi_id")

    if ensure_missing:
        missing = [sid for sid in species_ids if sid not in rows]
        for sid in missing:
            try:
                upsert_pokemon_from_api(sid)
            except Exception:
                pass
        if missing:
            rows = PokemonCache.objects.filter(
                pokeapi_id__in=species_ids
            ).in_bulk(field_name="pokeapi_id")

    out: List[Dict] = []
    for sid in species_ids:
        p = rows.get(sid)
        out.append({
            "id": sid,
            "name": (p.name if p else f"#{sid}"),
            "sprite": _sprite_url(sid),
        })
    return out