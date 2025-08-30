from django.db import models


class ApiResourceCache(models.Model):
    """
    Generic DB cache for PokeAPI endpoints.

    Stores raw payload + ETag/Last-Modified validators.
    Used where no dedicated domain model exists.
    """
    url = models.URLField(unique=True)
    payload = models.JSONField()
    etag = models.CharField(max_length=128, blank=True, default="")
    last_modified = models.CharField(max_length=128, blank=True, default="")
    fetched_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["fetched_at"]),
            models.Index(fields=["expires_at"]),
        ]