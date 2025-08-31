from django.urls import path
from .views import (
    TeamListView, TeamCreateView, TeamDetailView, TeamUpdateView, TeamDeleteView
)

app_name = "teams"
urlpatterns = [
    path("",              TeamListView.as_view(),   name="list"),
    path("new/",          TeamCreateView.as_view(), name="create"),
    path("<int:pk>/",     TeamDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/",TeamUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", TeamDeleteView.as_view(), name="delete"),
]