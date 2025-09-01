from django.contrib import admin
from .models import TeamLike, TeamComment


@admin.register(TeamComment)
class TeamCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("body", "author__username", "team__name")


@admin.register(TeamLike)
class TeamLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "team__name")