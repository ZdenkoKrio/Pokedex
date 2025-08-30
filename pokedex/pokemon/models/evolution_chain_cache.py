from django.db import models


class EvolutionChainCache(models.Model):
    """
    Minimal cache for evolution chains.

    Stores only the ordered list of species IDs.
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

    def __str__(self) -> str:
        return f"Chain #{self.chain_id}"