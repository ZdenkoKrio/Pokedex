from django.db import models


class EvolutionChainCache(models.Model):
    """
    Minimal cache pre evolučný chain: držíme len IDčka v požadovanom poradí.
    """
    chain_id = models.PositiveIntegerField(unique=True)
    species_ids = models.JSONField(default=list, blank=True)
    root_species_id = models.PositiveIntegerField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["chain_id"]),
            models.Index(fields=["root_species_id"]),
            models.Index(fields=["fetched_at"]),
        ]

    def __str__(self): return f"Chain #{self.chain_id}"
