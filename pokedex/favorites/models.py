from django.conf import settings
from django.db import models


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    pokemon_id = models.PositiveIntegerField()  # PokeAPI id
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
      unique_together = [("user", "pokemon_id")]
      indexes = [
        models.Index(fields=["user"]),
        models.Index(fields=["pokemon_id"]),
        models.Index(fields=["-created_at"]),
      ]

    def __str__(self):
        return f"{self.user} ♥ #{self.pokemon_id}"