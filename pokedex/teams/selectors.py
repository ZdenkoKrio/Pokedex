from __future__ import annotations
from django.db.models import QuerySet
from .models import Team


def my_teams(user) -> QuerySet[Team]:
    return Team.objects.filter(owner=user).prefetch_related("members")


def public_team_qs() -> QuerySet[Team]:
    return Team.objects.filter(is_public=True).prefetch_related("members")