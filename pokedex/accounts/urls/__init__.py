from django.urls import path, include

app_name = "accounts"

urlpatterns = [
    path("", include(("accounts.urls.auth", "accounts"), namespace="auth")),
    path("", include(("accounts.urls.profile", "accounts"), namespace="profile")),
    path("", include(("accounts.urls.password", "accounts"), namespace="password")),
]