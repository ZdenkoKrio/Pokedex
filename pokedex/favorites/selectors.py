from django.db.models import QuerySet
from .models import Favorite
from pokemon.models import PokemonCache


def user_favorite_ids(user) -> list[int]:
    """
    Return a list of PokeAPI IDs favorited by the given user.
    If user is anonymous, returns an empty list.
    """
    if not user or not user.is_authenticated:
        return []
    return list(Favorite.objects.filter(user=user).values_list("pokemon_id", flat=True))


def user_favorites_qs(user) -> QuerySet[PokemonCache]:
    """
    Return a queryset of PokemonCache objects that are favorited by the given user.
    Uses `user_favorite_ids` internally.
    """
    ids = user_favorite_ids(user)
    return PokemonCache.objects.filter(pokeapi_id__in=ids)


def is_favorite(user, pokeapi_id: int) -> bool:
    """
    Return True if the given Pokémon (by PokeAPI ID) is marked as favorite by the user.
    Returns False for anonymous users or when not favorited.
    """
    if not user or not user.is_authenticated:
        return False
    return Favorite.objects.filter(user=user, pokemon_id=pokeapi_id).exists()