from __future__ import annotations
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from .constants import MAX_TEAM_SIZE


class TeamMember(models.Model):
    """
    A single Pokémon placed in a team at a specific slot (1..6).
    Each Pokémon can appear only once per team, and each slot must be unique.
    """

    team = models.ForeignKey(
        "Team",
        on_delete=models.CASCADE,
        related_name="members",
    )
    slot = models.PositiveSmallIntegerField(help_text="1..6")
    pokemon_id = models.PositiveIntegerField(help_text="PokeAPI ID")

    class Meta:
        ordering = ["slot"]
        constraints = [
            models.UniqueConstraint(
                fields=["team", "slot"],
                name="teams_unique_slot_per_team",
            ),
            models.UniqueConstraint(
                fields=["team", "pokemon_id"],
                name="teams_unique_pokemon_in_team",
            ),
            models.CheckConstraint(
                name="teams_slot_in_range",
                check=Q(slot__gte=1) & Q(slot__lte=MAX_TEAM_SIZE),
            ),
        ]

    def clean(self):
        """Validate that slot is an integer between 1 and MAX_TEAM_SIZE."""
        if self.slot is None:
            return
        try:
            slot_int = int(self.slot)
        except (ValueError, TypeError):
            raise ValidationError({"slot": "Slot must be a number."})
        if not (1 <= slot_int <= MAX_TEAM_SIZE):
            raise ValidationError({"slot": f"Slot must be in 1..{MAX_TEAM_SIZE}."})

    def __str__(self) -> str:
        return f"{self.team} · slot {self.slot or '?'} · #{self.pokemon_id or '?'}"