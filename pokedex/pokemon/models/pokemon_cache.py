# pokemon/models/pokemon.py
from django.db import models
from .taxonomies import Type, Ability, Generation

class PokemonCache(models.Model):
    pokeapi_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=64, db_index=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    weight = models.PositiveIntegerField(null=True, blank=True)
    base_stats = models.JSONField(default=dict)

    # Nové polia pre filtre:
    generation = models.ForeignKey(
        Generation, null=True, blank=True, on_delete=models.SET_NULL, related_name="pokemon"
    )
    is_legendary = models.BooleanField(default=False)
    is_mythical = models.BooleanField(default=False)

    types = models.ManyToManyField(Type, related_name="pokemon", blank=True)
    abilities = models.ManyToManyField(Ability, related_name="pokemon", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pokeapi_id"]
        indexes = [
            models.Index(fields=["updated_at"]),
            models.Index(fields=["is_legendary"]),
            models.Index(fields=["is_mythical"]),
        ]

    def __str__(self):
        return f"#{self.pokeapi_id} {self.name}"