from __future__ import annotations
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView

from pokemon.models import PokemonCache, EvolutionChainCache
from pokemon.services.sync.evo.lookup import ensure_chain_for_species
from pokemon.selectors import evo_display_from_ids


class PokemonDetailView(TemplateView):
    template_name = "detail.html"

    def get(self, request, pokeapi_id: int, *args, **kwargs):
        p = (
            PokemonCache.objects
            .prefetch_related("types", "abilities")
            .filter(pokeapi_id=pokeapi_id)
            .first()
        )
        if not p:
            raise Http404("Pokémon not found in local cache.")

        chain = None

        if getattr(p, "evolution_chain_id", None):
            chain = EvolutionChainCache.objects.filter(chain_id=p.evolution_chain_id).first()

        if chain is None:
            try:
                chain = EvolutionChainCache.objects.filter(species_ids__contains=[p.pokeapi_id]).first()
            except Exception:
                chain = None

        if chain is None:
            chain_id = ensure_chain_for_species(p.pokeapi_id)
            if chain_id:
                chain = EvolutionChainCache.objects.filter(chain_id=chain_id).first()

        evo_list = []
        if chain:
            species_ids = list(chain.species_ids or [])
            evo_list = evo_display_from_ids(species_ids, ensure_missing=True)

        ctx = {"p": p, "evolution_chain": evo_list}
        return render(request, self.template_name, ctx)