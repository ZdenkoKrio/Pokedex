from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpRequest, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.html import escape

from teams.models import Team
from community.models import TeamComment


@login_required
@require_POST
def comment_create(request: HttpRequest, team_id: int) -> JsonResponse:
    """
    Create a new comment for a given team.

    Rules:
      - User must be logged in.
      - Only allowed on public teams, or private teams owned by the current user.
      - Body must be non-empty.
    """
    team = get_object_or_404(Team, pk=team_id)

    if not team.is_public and team.owner_id != request.user.id:
        raise Http404("Team not found.")

    body = (request.POST.get("body") or "").strip()
    if not body:
        return JsonResponse({"ok": False, "error": "empty_body"}, status=400)

    comment = TeamComment.objects.create(team=team, author=request.user, body=body)
    can_delete = request.user.has_perm("community.can_moderate_comments")

    return JsonResponse({
        "ok": True,
        "comment": {
            "id": comment.id,
            "author": request.user.username,
            "author_id": request.user.id,
            "body": escape(comment.body),
            "created_at": comment.created_at.isoformat(),
            "can_delete": can_delete,
        }
    })


@permission_required("community.can_moderate_comments", raise_exception=True)
@require_POST
def comment_delete(request: HttpRequest, comment_id: int) -> JsonResponse:
    """
    Delete an existing comment.

    Rules:
      - User must be logged in.
      - User must have `community.can_moderate_comments` permission.
    """
    comment = get_object_or_404(TeamComment, pk=comment_id)
    comment.delete()
    return JsonResponse({"ok": True})