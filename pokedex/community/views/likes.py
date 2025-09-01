from __future__ import annotations
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, Http404
from django.shortcuts import get_object_or_404

from teams.models import Team
from community.models import TeamLike


@login_required
def team_like_toggle(request: HttpRequest, team_id: int) -> JsonResponse:
    """
    Toggle like for a team.
    Only public teams (or private if owned by current user) are allowed.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method_not_allowed"}, status=405)

    team = get_object_or_404(Team, pk=team_id)

    # Security: only allow liking public teams or own private ones
    if not team.is_public and team.owner_id != request.user.id:
        raise Http404("Team not found.")

    obj, created = TeamLike.objects.get_or_create(team=team, user=request.user)
    if created:
        action = "liked"
    else:
        obj.delete()
        action = "unliked"

    likes = TeamLike.objects.filter(team=team).count()
    return JsonResponse({"ok": True, "action": action, "likes": likes})