from typing import Literal

SpriteSet = Literal[
    "default",
    "shiny",
    "official",
    "home",
    "home-shiny",
    "dream",
]

def sprite_url_for_id(pokeapi_id: int, set_name: SpriteSet = "default") -> str:
    """
    Return the sprite URL for a given Pokémon ID.

    set_name:
        - "default"      -> classic 96px PNG
        - "shiny"        -> shiny variant
        - "official"     -> official-artwork PNG (large)
        - "home"         -> home/normal PNG
        - "home-shiny"   -> home/shiny PNG
        - "dream"        -> dream-world SVG (not all species)
    """
    pid = int(pokeapi_id)
    base = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"

    mapping = {
        "default":    f"{base}/{pid}.png",
        "shiny":      f"{base}/shiny/{pid}.png",
        "official":   f"{base}/other/official-artwork/{pid}.png",
        "home":       f"{base}/other/home/{pid}.png",
        "home-shiny": f"{base}/other/home/shiny/{pid}.png",
        "dream":      f"{base}/other/dream-world/{pid}.svg",
    }

    return mapping.get(set_name, mapping["default"])