from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from teams.models import Team
from .mixins import OwnerRequiredMixin


class TeamDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    """Delete an existing team (only for owner)."""
    model = Team
    template_name = "teams/confirm_delete.html"
    success_url = reverse_lazy("teams:list")