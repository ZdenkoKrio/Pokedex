from typing import Sequence, Set
from pokemon.models import PokemonCache
from ..core.dbutils import db_have_values


def db_have_ids(ids: Sequence[int]) -> Set[int]:
    return db_have_values(PokemonCache, "pokeapi_id", ids)


def missing_after_chunk(chunk: Sequence[int]) -> Set[int]:
    return set(chunk) - db_have_ids(chunk)