from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from teams.forms import TeamForm, TeamMemberFormSet
from teams.models import Team
from .mixins import OwnerRequiredMixin, TeamPickHelpersMixin


class TeamCreateView(LoginRequiredMixin, TeamPickHelpersMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = "teams/form.html"
    success_url = reverse_lazy("teams:list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.method == "GET":
            ctx["formset"] = TeamMemberFormSet(instance=Team())
        self._inject_pick_helpers(ctx)
        return ctx

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()

        formset = TeamMemberFormSet(self.request.POST, instance=self.object)

        if formset.is_valid():
            formset.save()
            messages.success(self.request, "Team created.")
            return redirect(self.get_success_url())

        ctx = self.get_context_data(form=form)
        ctx["formset"] = formset
        return render(self.request, self.template_name, ctx)


class TeamUpdateView(LoginRequiredMixin, OwnerRequiredMixin, TeamPickHelpersMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = "teams/form.html"
    success_url = reverse_lazy("teams:list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.method == "GET":
            ctx["formset"] = TeamMemberFormSet(instance=self.object)
        self._inject_pick_helpers(ctx)
        return ctx

    def form_valid(self, form):
        self.object = form.save()
        formset = TeamMemberFormSet(self.request.POST, instance=self.object)

        if formset.is_valid():
            formset.save()
            messages.success(self.request, "Team updated.")
            return redirect(self.get_success_url())

        ctx = self.get_context_data(form=form)
        ctx["formset"] = formset
        return render(self.request, self.template_name, ctx)