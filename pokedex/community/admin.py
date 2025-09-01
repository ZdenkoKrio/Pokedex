# community/admin.py
from django.contrib import admin
from .models import TeamLike

@admin.register(TeamLike)
class TeamLikeAdmin(admin.ModelAdmin):
    list_display = ("team", "user", "created_at")
    search_fields = ("team__name", "user__username")
    list_filter = ("created_at",)