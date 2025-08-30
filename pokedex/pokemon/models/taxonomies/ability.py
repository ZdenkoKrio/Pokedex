from django.db import models


class Ability(models.Model):
    """
    Ability taxonomy (e.g. Levitate, Overgrow).

    Used for filtering and display. Synced from PokeAPI.
    """
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.name