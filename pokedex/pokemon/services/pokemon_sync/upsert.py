from __future__ import annotations
"""
Upsert a single Pokémon into the local cache (DB).
"""

from typing import Callable, List, Optional, Sequence, Tuple

from django.db import transaction
from pokemon.models import PokemonCache, Type, Ability, Generation
from pokemon.services.api import get_json, url
from .normalize import (
    stat_dict,
    taxonomy_slugs_from_payload,
    species_payload_for,
)

LogFn = Optional[Callable[[str], None]]  # e.g. lambda s: stdout.write(s + "\n")


def _existing_ids_for(model, slugs: Sequence[str]) -> Tuple[List[int], List[str]]:
    """
    Return (existing_ids, missing_slugs) for the given taxonomy model and slugs.
    Does NOT create anything.
    """
    if not slugs:
        return [], []
    rows = model.objects.filter(slug__in=slugs).values_list("id", "slug")
    found_ids = [rid for rid, _ in rows]
    found_slugs = {s for _, s in rows}
    missing = [s for s in slugs if s not in found_slugs]
    return found_ids, missing


def _generation_from_species(species: dict) -> Tuple[Optional[Generation], Optional[str]]:
    """
    Find Generation object by slug from species payload. Does NOT create anything.

    Returns
    -------
    (generation_obj_or_none, missing_slug_or_none)
    """
    gen_slug = ((species.get("generation") or {}).get("name")) or None
    if not gen_slug:
        return None, None
    obj = Generation.objects.filter(slug=gen_slug).first()
    return obj, (None if obj else gen_slug)


def _warn(log: LogFn, msg: str) -> None:
    if log:
        log(msg)


@transaction.atomic
def upsert_pokemon_from_api(
    id_or_name: str | int,
    *,
    logger: LogFn = None,
) -> PokemonCache:
    """
    Fetch a Pokémon from PokeAPI and upsert it into the local thin cache.

    Behavior
    --------
    - Does NOT create taxonomies (Type/Ability/Generation). It only links to ones
      already present in DB. Missing slugs are reported via `logger`.

    Parameters
    ----------
    id_or_name : int | str
        PokeAPI identifier (e.g. 25 or "pikachu").
    logger : callable | None
        Optional sink for warnings (e.g. `self.stdout.write`).

    Returns
    -------
    PokemonCache
        The upserted instance.
    """
    # 1) `/pokemon/<id-or-name>`
    d = get_json(url("pokemon", id_or_name))

    # 2) species → generation/flags
    species = species_payload_for(d)
    gen_obj, missing_gen = _generation_from_species(species)
    is_legendary = bool(species.get("is_legendary", False))
    is_mythical = bool(species.get("is_mythical", False))

    # 3) Base row
    p, _ = PokemonCache.objects.update_or_create(
        pokeapi_id=d["id"],
        defaults={
            "name": d.get("name") or "",
            "height": d.get("height"),
            "weight": d.get("weight"),
            "base_stats": stat_dict(d.get("stats") or []),
            "generation": gen_obj,  # may be None if generation not synced yet
            "is_legendary": is_legendary,
            "is_mythical": is_mythical,
        },
    )

    # 4) M2M: link ONLY existing taxonomies
    type_slugs, ability_slugs = taxonomy_slugs_from_payload(d)
    type_ids, missing_types = _existing_ids_for(Type, type_slugs)
    ability_ids, missing_abilities = _existing_ids_for(Ability, ability_slugs)

    if type_ids:
        p.types.set(type_ids)
    else:
        p.types.clear()

    if ability_ids:
        p.abilities.set(ability_ids)
    else:
        p.abilities.clear()

    # granular warnings (easy to grep in logs)
    for mt in missing_types:
        _warn(logger, f"[warn] Missing Type '{mt}' for Pokémon #{p.pokeapi_id} {p.name}")

    for ma in missing_abilities:
        _warn(logger, f"[warn] Missing Ability '{ma}' for Pokémon #{p.pokeapi_id} {p.name}")

    if missing_gen:
        _warn(logger, f"[warn] Missing Generation '{missing_gen}' for Pokémon #{p.pokeapi_id} {p.name}")

    return p