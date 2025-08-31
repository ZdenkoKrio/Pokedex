from __future__ import annotations
from django.conf import settings
from django.db import models


class Team(models.Model):
    """
    A team of up to MAX_TEAM_SIZE Pokémon.
    Owned by a single user, can be public or private.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teams",
    )
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="teams_unique_owner_name",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.owner})"

    @property
    def size(self) -> int:
        """Return number of members currently in the team."""
        return self.members.count()