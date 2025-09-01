from django import template

register = template.Library()

BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"

@register.filter
def sprite_url(poke_id: int, mode: str = "default") -> str:
    sid = str(poke_id)
    m = (mode or "default").lower()
    if m == "shiny":
        return f"{BASE}/shiny/{sid}.png"
    if m == "animated":
        return f"{BASE}/versions/generation-v/black-white/animated/{sid}.gif"
    if m == "artwork":
        return f"{BASE}/other/official-artwork/{sid}.png"
    return f"{BASE}/{sid}.png"