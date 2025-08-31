from django import template
from favorites.selectors import is_favorite


register = template.Library()


@register.simple_tag(takes_context=True)
def fav_is(context, pokeapi_id):
    """Usage: {% fav_is p.pokeapi_id as f %}{% if f %}...{% endif %}"""
    request = context.get("request")
    user = getattr(request, "user", None)
    return is_favorite(user, pokeapi_id)