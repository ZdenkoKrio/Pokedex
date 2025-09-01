from django.db.models import Count, Exists, OuterRef, QuerySet
from teams.models import Team
from .models import TeamLike
from .models import TeamComment


def comments_for_team(team_id: int) -> QuerySet[TeamComment]:
    return (
        TeamComment.objects
        .select_related("author")
        .filter(team_id=team_id)
        .order_by("-created_at")
    )


def public_teams_qs(for_user=None) -> QuerySet[Team]:
    """
    Return all public teams annotated with:
      - likes_count: total likes
      - is_liked: whether `for_user` has liked the team
    """
    base = Team.objects.filter(is_public=True).prefetch_related("members", "owner")
    base = base.annotate(likes_count=Count("likes", distinct=True))

    if for_user and getattr(for_user, "is_authenticated", False):
        like_subq = TeamLike.objects.filter(team=OuterRef("pk"), user=for_user)
        base = base.annotate(is_liked=Exists(like_subq))
    else:
        base = base.annotate(is_liked=Count("likes") * 0)

    return base


def user_public_teams_qs(user, for_user=None) -> QuerySet[Team]:
    """
    Return all public teams of a given user annotated with:
      - likes_count: total likes
      - is_liked: whether `for_user` has liked the team
    """
    qs = Team.objects.filter(owner=user, is_public=True).prefetch_related("members")
    qs = qs.annotate(likes_count=Count("likes", distinct=True))

    if for_user and getattr(for_user, "is_authenticated", False):
        like_subq = TeamLike.objects.filter(team=OuterRef("pk"), user=for_user)
        qs = qs.annotate(is_liked=Exists(like_subq))
    else:
        qs = qs.annotate(is_liked=Count("likes") * 0)

    return qs