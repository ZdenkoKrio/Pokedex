from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import SignupView


urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/",  auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="pokemon:pokemon_list"), name="logout"),
]