import pytest
from pokemon.services.api import url


@pytest.mark.django_db
def test_build_url():
    assert url("pokemon", 25) == "https://pokeapi.co/api/v2/pokemon/25/"
    assert url("type") == "https://pokeapi.co/api/v2/type/"
    # trimming/slashes robustness
    assert url("/pokemon/", "/1/") == "https://pokeapi.co/api/v2/pokemon/1/"