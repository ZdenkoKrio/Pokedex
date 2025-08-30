from __future__ import annotations

BASE = "https://pokeapi.co/api/v2"


def url(*parts: object) -> str:
    """
    Build a PokeAPI URL by joining path segments and ensuring a trailing slash.

    Example
    -------
    url("pokemon", 25) -> "https://pokeapi.co/api/v2/pokemon/25/"
    """
    return "/".join([BASE.strip("/")] + [str(p).strip("/") for p in parts]) + "/"