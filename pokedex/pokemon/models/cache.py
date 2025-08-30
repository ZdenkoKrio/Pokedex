from django.db import models


class ApiResourceCache(models.Model):
    """
    Generická DB cache pre PokeAPI URL.
    Používa sa pre listy (pagination), type/ability listing, species… – všade tam, kde nemáme doménový model.
    """
    url = models.URLField(unique=True)
    payload = models.JSONField()
    etag = models.CharField(max_length=128, blank=True, default="")
    last_modified = models.CharField(max_length=128, blank=True, default="")
    fetched_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["fetched_at"]), models.Index(fields=["expires_at"])]
        