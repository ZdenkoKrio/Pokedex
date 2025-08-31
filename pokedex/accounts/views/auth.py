from __future__ import annotations
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView

from accounts.forms import SignupForm

User = get_user_model()


class MeRedirectView(LoginRequiredMixin, RedirectView):
    """
    Redirect authenticated users who hit public auth pages.

    Use-case:
      If a signed-in user opens /signup, send them to their profile dashboard
      instead of showing the sign-up form again.
    """
    pattern_name = "accounts:me"


class SignupView(FormView):
    """
    Simple user sign-up flow.

    - Renders a standard SignupForm.
    - On success: creates the user, logs them in, flashes a message,
      and redirects to the profile page.
    """
    template_name = "signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("accounts:me")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return MeRedirectView.as_view()(request, *args, **kwargs)
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Welcome! Your account was created.")
        return super().form_valid(form)