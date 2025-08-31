from django.urls import path
from .views.api import ToggleFavoriteView
from .views.pages import MyFavoritesView


app_name = "favorites"

urlpatterns = [
    path("toggle/<int:pokeapi_id>/", ToggleFavoriteView.as_view(), name="toggle"),
    path("mine/", MyFavoritesView.as_view(), name="mine"),
]