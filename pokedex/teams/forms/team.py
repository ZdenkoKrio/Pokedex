from __future__ import annotations
from django import forms
from teams.models import Team


class TeamForm(forms.ModelForm):
    """Basic form for creating/updating a team (without members)."""

    class Meta:
        model = Team
        fields = ("name", "description", "is_public")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }