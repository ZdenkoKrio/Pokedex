from django.contrib import admin
from .models import Team, TeamMember

class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0
    fields = ("slot", "pokemon_id")
    ordering = ("slot",)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_public", "size", "updated_at")
    list_filter = ("is_public",)
    search_fields = ("name", "owner__username")
    inlines = [TeamMemberInline]