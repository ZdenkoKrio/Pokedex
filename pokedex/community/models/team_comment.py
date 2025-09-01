from django.conf import settings
from django.db import models


class TeamComment(models.Model):
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="team_comments")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["team", "-created_at"]),
            models.Index(fields=["author", "-created_at"]),
        ]
        permissions = [
            ("can_moderate_comments", "Can moderate (delete) team comments"),
        ]

    def __str__(self) -> str:
        return f"Comment by {self.author} on team {self.team_id}"