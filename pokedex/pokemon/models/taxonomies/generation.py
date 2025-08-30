from django.db import models


class Generation(models.Model):
    """
    Pokémon generation taxonomy (e.g. Generation I).

    Simple reference table for filtering and display.
    """
    slug = models.SlugField(unique=True)  # e.g. "generation-i"
    name = models.CharField(max_length=64)  # e.g. "Generation I"

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.name