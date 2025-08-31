from __future__ import annotations
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

User = get_user_model()


class SignupForm(UserCreationForm):
    """Signup: username + email + password1/2 (z UserCreationForm)."""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class UserForm(forms.ModelForm):
    """Edit základných údajov účtu (meno, email, username)."""
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "f-input"}),
            "last_name":  forms.TextInput(attrs={"class": "f-input"}),
            "username":   forms.TextInput(attrs={"class": "f-input"}),
            "email":      forms.EmailInput(attrs={"class": "f-input"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class ProfileForm(forms.ModelForm):
    """Edit profilových údajov (zachované tvoje polia)."""
    class Meta:
        model = Profile
        fields = ("display_name", "bio", "avatar", "is_public")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us about yourself…", "class": "f-input"}),
        }

    def clean_avatar(self):
        f = self.cleaned_data.get("avatar")
        if f and f.size > 3 * 1024 * 1024:  # 3 MB limit
            raise forms.ValidationError("Avatar is too large (max 3MB).")
        return f