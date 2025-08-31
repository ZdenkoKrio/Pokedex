from django.urls import path, include

app_name = "accounts"

urlpatterns = [
    path("", include("accounts.urls.auth")),
    path("", include("accounts.urls.profile")),
    path("", include("accounts.urls.password")),
]