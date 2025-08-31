from __future__ import annotations
from django import forms
from teams.models import TeamMember


class TeamMemberForm(forms.ModelForm):
    """
    Form for a single team slot.
    - pokemon_id is optional; empty rows are dropped by the formset.
    """
    pokemon_id = forms.IntegerField(required=False, min_value=1)

    class Meta:
        model = TeamMember
        fields = ("slot", "pokemon_id")

    def clean(self):
        # No extra validation here; range & duplicates are handled in the formset.
        return super().clean()