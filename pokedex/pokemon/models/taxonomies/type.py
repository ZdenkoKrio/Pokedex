from django.db import models


class Type(models.Model):
    """
    Pokémon type taxonomy (Fire, Water, Grass...).

    Minimal subset required for filters and UI.
    """
    slug = models.SlugField(max_length=32, unique=True)  # "fire"
    name = models.CharField(max_length=32)  # "Fire"

    def __str__(self) -> str:
        return self.name