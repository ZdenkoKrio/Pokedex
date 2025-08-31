from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from teams.models import Team


class TeamListView(LoginRequiredMixin, ListView):
    """Show list of user's teams (with members prefetched)."""
    model = Team
    template_name = "teams/list.html"
    context_object_name = "teams"

    def get_queryset(self):
        return (
            Team.objects
            .filter(owner=self.request.user)
            .prefetch_related("members")
        )