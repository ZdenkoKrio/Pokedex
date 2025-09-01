from django.urls import path
from .views import PublicUsersView, PublicTeamsView, PublicUserDetailView, team_like_toggle


app_name = "community"
urlpatterns = [
    path("users/", PublicUsersView.as_view(), name="users"),
    path("users/<int:user_id>/", PublicUserDetailView.as_view(), name="user_detail"),
    path("teams/", PublicTeamsView.as_view(), name="teams"),

    path("teams/<int:team_id>/like/", team_like_toggle, name="team_like_toggle"),
]