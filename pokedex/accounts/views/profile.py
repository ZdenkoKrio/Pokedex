from __future__ import annotations
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import View
from django.shortcuts import render, redirect
from pokemon.utils.sprites import sprite_url_for_id
from favorites.selectors import user_favorites_qs
from accounts.forms import ProfileForm, UserForm


class ProfileDetailView(LoginRequiredMixin, View):
    """
    Read-only profile dashboard for the current user.

    Template: accounts/me.html
    Context:
      - profile: request.user.profile
      - user:    request.user
    """
    template_name = "me.html"

    def get(self, request, *args, **kwargs):
        # vezmeme prvých 6 obľúbencov na náhľad
        fav_qs = user_favorites_qs(request.user).prefetch_related("types")[:6]
        favorites_preview = [{
            "id": p.pokeapi_id,
            "name": p.name,
            "sprite": sprite_url_for_id(p.pokeapi_id, "default"),
            "types": [t.slug for t in p.types.all()],
        } for p in fav_qs]

        return render(request, self.template_name, {
            "profile": request.user.profile,
            "user": request.user,
            "favorites_preview": favorites_preview,
            "favorites_total": user_favorites_qs(request.user).count(),
        })


class ProfileEditView(LoginRequiredMixin, View):
    """
    Separate edit screen for account + profile.

    - Shows two forms on a single page:
        * UserForm (first/last name, username, email, …)
        * ProfileForm (display_name, bio, avatar, is_public, …)
    - On POST: validates both, saves, flashes a message, redirects back to /me.

    Template: accounts/me_edit.html
    """
    template_name = "me_edit.html"
    success_url = reverse_lazy("accounts:me")

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            "user_form": UserForm(instance=request.user),
            "profile_form": ProfileForm(instance=request.user.profile),
            "profile": request.user.profile,
        })

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated.")
            return redirect(self.success_url)

        messages.error(request, "Please fix the errors below.")
        return render(request, self.template_name, {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile": request.user.profile,
        })