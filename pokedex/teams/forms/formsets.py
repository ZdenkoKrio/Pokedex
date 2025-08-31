from __future__ import annotations
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.core.exceptions import ValidationError
from teams.models import Team, TeamMember, MAX_TEAM_SIZE
from .member import TeamMemberForm


class BaseTeamMemberFormSet(BaseInlineFormSet):
    """
    - Marks rows without pokemon_id as DELETE=True (ignored on save).
    - Validates slot range (1..MAX_TEAM_SIZE) and duplicate slots.
    """

    def clean(self):
        super().clean()

        used_slots = set()

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            cd = form.cleaned_data
            if cd.get("DELETE"):
                continue  # skip explicitly deleted rows

            pid = cd.get("pokemon_id")
            slot = cd.get("slot")

            # Empty member -> drop it
            if not pid:
                cd["DELETE"] = True
                continue

            # Validate slot
            try:
                s = int(slot)
            except (TypeError, ValueError):
                raise ValidationError("Each selected member must have a valid slot number.")

            if not (1 <= s <= MAX_TEAM_SIZE):
                raise ValidationError(f"Slot must be between 1 and {MAX_TEAM_SIZE}.")

            if s in used_slots:
                raise ValidationError("Duplicate slots are not allowed.")
            used_slots.add(s)


TeamMemberFormSet = inlineformset_factory(
    Team,
    TeamMember,
    form=TeamMemberForm,
    formset=BaseTeamMemberFormSet,
    fields=("slot", "pokemon_id"),
    extra=MAX_TEAM_SIZE,     # always show 6 rows
    max_num=MAX_TEAM_SIZE,   # forbid more than 6
    can_delete=True,
    validate_max=True,
)