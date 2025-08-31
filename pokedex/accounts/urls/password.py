from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Password change
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="password/password_change_form.html",
            success_url=reverse_lazy("accounts:password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="password/password_change_done.html"
        ),
        name="password_change_done",
    ),

    # Password reset (forgot password)
    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password/password_reset_form.html",
            email_template_name="password/password_reset_email.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]