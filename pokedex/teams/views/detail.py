from __future__ import annotations
from typing import Dict, List, Tuple

from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from teams.models import Team
from community.models import TeamLike
from community.selectors import comments_for_team
from pokemon.models import PokemonCache
from pokemon.utils.sprites import sprite_url_for_id


class TeamDetailView(TemplateView):
    """
    Display detail of a single team with members, stats, and like metadata.
    Built on TemplateView for better decomposition into helper methods.
    """
    template_name = "teams/detail.html"
    context_object_name = "team"

    # ---------- Queryset & object ----------

    def get_base_queryset(self):
        """
        Base queryset for Team with owner, members, and likes_count annotation.
        """
        return (
            Team.objects
            .select_related("owner")
            .prefetch_related("members")
            .annotate(likes_count=Count("likes", distinct=True))
        )

    def filter_for_request(self, qs):
        """
        Apply visibility rules:
        - anonymous: only public teams
        - authenticated: public + own private teams
        """
        user = self.request.user
        if user.is_authenticated:
            return qs.filter(Q(is_public=True) | Q(owner=user))
        return qs.filter(is_public=True)

    def get_object(self):
        """
        Return Team object for given PK or 404 if not accessible.
        """
        pk = self.kwargs.get("pk")
        if pk is None:
            raise Http404("Team not found.")
        qs = self.filter_for_request(self.get_base_queryset())
        return get_object_or_404(qs, pk=pk)

    # ---------- Domain logic ----------

    def build_members_and_stats(self, team: Team) -> Tuple[List[dict], List[str]]:
        """
        Build members and stats:
          - members: list of dicts (id, name, sprite, stats)
          - stats_keys: ordered list of stat keys
        """
        member_ids = list(team.members.values_list("pokemon_id", flat=True))
        db_pokemon = (
            PokemonCache.objects
            .filter(pokeapi_id__in=member_ids)
            .prefetch_related("types")
        )
        by_id: Dict[int, PokemonCache] = {p.pokeapi_id: p for p in db_pokemon}

        members: List[dict] = []
        discovered = set()

        for tm in team.members.all().order_by("slot"):
            p = by_id.get(tm.pokemon_id)
            if not p:
                continue
            base_stats = p.base_stats or {}
            discovered.update(base_stats.keys())
            members.append({
                "id": p.pokeapi_id,
                "name": p.name,
                "sprite": sprite_url_for_id(p.pokeapi_id, "default"),
                "stats": {k: int(base_stats.get(k, 0) or 0) for k in base_stats.keys()},
            })

        preferred = ("hp", "attack", "defense", "special-attack", "special-defense", "speed")
        stats_keys = [k for k in preferred if k in discovered] + sorted(
            k for k in discovered if k not in preferred
        )
        return members, stats_keys

    def build_like_meta(self, team: Team) -> dict:
        """
        Build like metadata:
          - likes_count: total likes
          - is_liked: whether current user liked
          - likers: latest users who liked
          - can_like: whether like button should be shown
        """
        user = self.request.user
        is_liked = False
        if user.is_authenticated:
            is_liked = TeamLike.objects.filter(team=team, user=user).exists()

        likers_qs = (
            TeamLike.objects
            .filter(team=team)
            .select_related("user")
            .order_by("-id")[:12]
        )
        likers = [{"id": tl.user_id, "username": tl.user.username} for tl in likers_qs]

        can_like = team.is_public or (user.is_authenticated and team.owner_id == user.id)

        return {
            "likes_count": getattr(team, "likes_count", 0),
            "is_liked": is_liked,
            "likers": likers,
            "can_like": can_like,
        }

    # ---------- TemplateView interface ----------

    def get_context_data(self, **kwargs):
        """
        Return template context with:
          - team object
          - members and stats
          - like metadata
        """
        ctx = super().get_context_data(**kwargs)
        team = self.get_object()

        members, stats_keys = self.build_members_and_stats(team)
        like_meta = self.build_like_meta(team)

        ctx["comments"] = list(comments_for_team(team.id))
        ctx["can_moderate_comments"] = (
                self.request.user.is_authenticated and
                self.request.user.groups.filter(name="community_admins").exists()
        )

        ctx[self.context_object_name] = team
        ctx["members"] = members
        ctx["stats_keys"] = stats_keys
        ctx.update(like_meta)
        return ctx