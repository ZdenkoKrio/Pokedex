from django.db import models


class Generation(models.Model):
    slug = models.SlugField(unique=True)          # e.g. "generation-i"
    name = models.CharField(max_length=64)        # e.g. "Generation I"

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name