from django.conf import settings
from django.db import models


class TeamLike(models.Model):
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="likes", db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="team_likes", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["team", "user"], name="uniq_team_user_like"),
        ]
        indexes = [
            models.Index(fields=["team", "-created_at"], name="idx_like_team_recent"),
            models.Index(fields=["user", "-created_at"], name="idx_like_user_recent"),
        ]

    def __str__(self):
        return f"{self.user} ♥ {self.team}"