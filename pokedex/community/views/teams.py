from __future__ import annotations
from django.db.models import Count, Exists, OuterRef, Value, BooleanField
from django.views.generic import ListView

from teams.models import Team
from community.models import TeamLike
from .utils import build_members_preview


class PublicTeamsView(ListView):
    """
    Public list of teams, with preview of up to 6 Pokémon.
    Also annotates likes_count and is_liked (for current user).
    """
    template_name = "teams.html"
    context_object_name = "teams"

    def get_queryset(self):
        qs = (
            Team.objects
            .filter(is_public=True)
            .select_related("owner")
            .prefetch_related("members")
            .order_by("-updated_at", "-id")
            .annotate(likes_count=Count("likes", distinct=True))
        )
        if self.request.user.is_authenticated:
            sub = TeamLike.objects.filter(team=OuterRef("pk"), user=self.request.user)
            qs = qs.annotate(is_liked=Exists(sub))
        else:
            qs = qs.annotate(is_liked=Value(False, output_field=BooleanField()))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        build_members_preview(ctx["teams"])
        return ctx