from __future__ import annotations
from typing import Dict, Any, List
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView

from pokemon.models import PokemonCache, EvolutionChainCache
from pokemon.services.cache.evo.lookup import ensure_chain_for_species
from pokemon.selectors import evo_display_from_ids
from favorites.models import Favorite

from pokemon.services.api import get_json, url
from pokemon.services.detail import (
    fetch_species,
    normalize_species,
    fetch_encounters,
    extract_pokemon_moves,
    annotate_some_moves,
    sprite_bundle,
    flavor_bundle,
    build_varieties_strip,
)


class PokemonDetailView(TemplateView):
    template_name = "detail.html"

    # ---------- helpers ----------
    def _resolve_species(self, any_id: int) -> int:
        try:
            spec = fetch_species(any_id)  # už je to species id
            return int(spec.get("id") or any_id), spec

        except Exception:
            raw = get_json(url("pokemon", any_id))
            spec_url = (raw.get("species") or {}).get("url")

            if not spec_url:
                raise Http404("Pokémon species not found.")

            species_id = int(str(spec_url).rstrip("/").split("/")[-1])
            spec = fetch_species(species_id)
            return species_id, spec


    def _evolution_list(self, species_id: int) -> List[dict]:
        try:
            chain = EvolutionChainCache.objects.filter(species_ids__contains=[species_id]).first()
        except Exception:
            chain = None

        if chain is None:
            chain_id = ensure_chain_for_species(species_id)
            if chain_id:
                chain = EvolutionChainCache.objects.filter(chain_id=chain_id).first()

        return evo_display_from_ids(list(chain.species_ids or []), ensure_missing=True) if chain else []


    def _favorite_state(self, request, species_id: int) -> Dict[str, Any]:
        is_fav = request.user.is_authenticated and Favorite.objects.filter(
            user=request.user, pokemon_id=species_id
        ).exists()
        return {"is_fav": is_fav}

    # ---------- GET ----------
    def get(self, request, pokeapi_id: int, *args, **kwargs):
        any_id = int(pokeapi_id)
        species_id, species_raw = self._resolve_species(any_id)

        p = (
            PokemonCache.objects
            .prefetch_related("types", "abilities")
            .filter(pokeapi_id=species_id)
            .first()
        )
        if not p:
            raise Http404("Pokémon not found in local cache.")

        sprite_mode, sprite_urls = sprite_bundle(any_id, request.GET.get("sprite"))

        species = normalize_species(species_raw)

        flavor = flavor_bundle(species_raw, request.GET.get("fv"))

        try:
            encounters = fetch_encounters(species_id)

        except Exception:
            encounters = []

        evolution_chain = self._evolution_list(species_id)

        pokemon_raw = get_json(url("pokemon", any_id))
        req_vg = request.GET.get("vg") or None
        grouped, available_vgs, active_vg = extract_pokemon_moves(pokemon_raw, version_group=req_vg)
        grouped = annotate_some_moves(grouped, per_group=10)

        varieties_strip = build_varieties_strip(species, current_any_id=any_id)

        ctx = {
            "p": p,
            "primary": p.types.first(),
            "sprite_mode": sprite_mode,
            "sprite_urls": sprite_urls,

            "species": species,
            "encounters": encounters,
            "evolution_chain": evolution_chain,

            "moves_groups": grouped,
            "moves_vgs": available_vgs,
            "moves_active_vg": active_vg,

            "flavor_entries": flavor["entries"],
            "flavor_active": flavor["active"],

            "varieties_strip": varieties_strip,

            **self._favorite_state(request, species_id),
        }
        return render(request, self.template_name, ctx)