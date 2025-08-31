from __future__ import annotations
from typing import Optional
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.views.generic import TemplateView
from pokemon.forms import PokemonFilterForm
from pokemon.selectors import list_pokemon


def _tri_state(val) -> Optional[bool]:
    if val in (True, "true", "yes", "1", 1): return True
    if val in (False, "false", "no", "0", 0): return False
    return None


class PokemonListView(TemplateView):
    template_name = "list.html"
    PER_PAGE = 50

    def get(self, request, *args, **kwargs):
        form = PokemonFilterForm(request.GET)
        form.is_valid()
        cd = form.cleaned_data

        type_obj    = cd.get("type")
        ability_obj = cd.get("ability")
        gen_obj     = cd.get("generation")

        qs = list_pokemon(
            search=cd.get("q"),
            type_slug=(type_obj.slug if type_obj else None),
            ability_slug=(ability_obj.slug if ability_obj else None),
            generation_slug=(gen_obj.slug if gen_obj else None),
            min_weight=cd.get("min_weight"),
            max_weight=cd.get("max_weight"),
            legendary=_tri_state(cd.get("legendary")),
            mythical=_tri_state(cd.get("mythical")),
        )

        raw_page = cd.get("page") or request.GET.get("page") or 1
        try:
            page_num = int(raw_page)
        except (TypeError, ValueError):
            page_num = 1

        paginator = Paginator(qs, self.PER_PAGE)
        try:
            page_obj = paginator.page(page_num)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.page(1)

        params = request.GET.copy()
        params.pop("page", None)
        base_qs = params.urlencode()

        ctx = {
            "form": form,
            "items": page_obj.object_list,
            "is_paginated": paginator.num_pages > 1,
            "page_obj": page_obj,
            "paginator": paginator,
            "total": paginator.count,
            "base_qs": base_qs,
        }
        return render(request, self.template_name, ctx)