from __future__ import annotations
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Value, BooleanField
from django.views.generic import ListView, TemplateView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from teams.models import Team
from community.models import TeamLike
from .utils import build_members_preview

User = get_user_model()


class PublicUsersView(ListView):
    template_name = "users.html"
    context_object_name = "users"
    paginate_by = 50

    def get_queryset(self):
        return (
            User.objects
            .filter(teams__is_public=True)
            .distinct()
            .annotate(public_teams=Count("teams", filter=Q(teams__is_public=True)))
            .order_by("username")
        )



class PublicUserDetailView(TemplateView):
    """
    Public profile for a user, showing only their public teams.
    Annotates each team with likes_count and is_liked (for current user).
    """
    template_name = "user_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile_user = get_object_or_404(User, pk=kwargs["user_id"])

        teams = (
            Team.objects
            .filter(owner=profile_user, is_public=True)
            .prefetch_related("members")
            .order_by("-updated_at")
            .annotate(likes_count=Count("likes", distinct=True))
        )
        if self.request.user.is_authenticated:
            sub = TeamLike.objects.filter(team=OuterRef("pk"), user=self.request.user)
            teams = teams.annotate(is_liked=Exists(sub))
        else:
            teams = teams.annotate(is_liked=Value(False, output_field=BooleanField()))

        build_members_preview(teams)

        ctx["profile_user"] = profile_user
        ctx["teams"] = teams
        return ctx