from django.urls import path
from .views import PokemonListView, PokemonDetailView


app_name = "pokemon"

urlpatterns = [
    path("", PokemonListView.as_view(), name="pokemon_list"),
    path("<int:pokeapi_id>/", PokemonDetailView.as_view(), name="pokemon_detail"),
]