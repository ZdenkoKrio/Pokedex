from django.db import models


class Type(models.Model):
    """Taxonómia Pokémon typov (Fire, Water…). Udržiava sa len to, čo potrebujeme na filtre/UI."""
    slug = models.SlugField(max_length=32, unique=True)     # "fire"
    name = models.CharField(max_length=32)                  # "Fire"

    def __str__(self): return self.name
