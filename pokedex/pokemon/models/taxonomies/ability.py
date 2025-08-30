from django.db import models


class Ability(models.Model):
    """Taxonómia schopností (Levitate, Overgrow…). Primárne pre filtrovanie a zobrazenie názvov."""
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=64)

    def __str__(self): return self.name
