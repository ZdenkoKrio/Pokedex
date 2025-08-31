from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150, blank=True)
    is_public = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        default="defaults/default-avatar.png",
        blank=True,
    )

    def __str__(self):
        return f"Profile of {self.user.username}"