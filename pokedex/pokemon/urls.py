from django.urls import path
from .views import *


app_name = "pokemon"

urlpatterns = [
    path("", PokemonListView.as_view(), name="pokemon_list"),
    path("<int:pokeapi_id>/", PokemonDetailView.as_view(), name="pokemon_detail"),
    path("compare/", CompareView.as_view(), name="compare"),
    path("compare/toggle/<int:pokeapi_id>/", compare_toggle, name="compare_toggle"),
]