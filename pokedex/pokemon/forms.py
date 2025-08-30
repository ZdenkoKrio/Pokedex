from __future__ import annotations
from django import forms
from pokemon.models import Type, Ability, Generation
from pokemon.services.taxonomy import ensure_types, ensure_abilities, ensure_generations


TRI_STATE_CHOICES = (
    ("", "— any —"),
    ("true", "Yes"),
    ("false", "No"),
)


class PokemonFilterForm(forms.Form):
    q = forms.CharField(
        label="Search (name or id)",
        required=False,
        help_text="You can write a name or exact Pokédex ID.",
        widget=forms.TextInput(attrs={"placeholder": "e.g. pikachu or 25", "class": "f-input"}),
    )

    type = forms.ModelChoiceField(
        queryset=Type.objects.none(),  # nastaví sa v __init__
        required=False,
        empty_label="— by type —",
        widget=forms.Select(attrs={"class": "f-select"}),
    )
    ability = forms.ModelChoiceField(
        queryset=Ability.objects.none(),
        required=False,
        empty_label="— by ability —",
        widget=forms.Select(attrs={"class": "f-select"}),
    )
    generation = forms.ModelChoiceField(
        queryset=Generation.objects.none(),
        required=False,
        empty_label="— by generation —",
        widget=forms.Select(attrs={"class": "f-select"}),
    )

    # tri-state ako str, v selektoroch potom prevedieme cez cleaned_bool()
    legendary = forms.ChoiceField(
        required=False,
        label="Legendary",
        choices=TRI_STATE_CHOICES,
        widget=forms.Select(attrs={"class": "f-select"}),
    )
    mythical = forms.ChoiceField(
        required=False,
        label="Mythical",
        choices=TRI_STATE_CHOICES,
        widget=forms.Select(attrs={"class": "f-select"}),
    )

    min_weight = forms.IntegerField(
        required=False,
        min_value=0,
        label="Min weight",
        help_text="In hectograms (PokeAPI units).",
        widget=forms.NumberInput(attrs={"placeholder": "0", "class": "f-input"}),
    )
    max_weight = forms.IntegerField(
        required=False,
        min_value=0,
        label="Max weight",
        help_text="In hectograms (PokeAPI units).",
        widget=forms.NumberInput(attrs={"placeholder": "1000", "class": "f-input"}),
    )

    page = forms.IntegerField(required=False, min_value=1, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ensure_types()
        ensure_abilities()
        ensure_generations()
        self.fields["type"].queryset = Type.objects.all().order_by("name")
        self.fields["ability"].queryset = Ability.objects.all().order_by("name")
        self.fields["generation"].queryset = Generation.objects.all().order_by("name")

    def cleaned_bool(self, name: str) -> bool | None:
        """
        Preveď 'true'/'false'/'' z ChoiceField na bool/None pre selektory.
        """
        val = self.cleaned_data.get(name)
        if val == "true":
            return True

        if val == "false":
            return False

        return None