from django import template

register = template.Library()


@register.filter(name="get")
def dict_get(d, key):
    """Safe dict lookup usable in templates: {{ mydict|get:"special-attack" }}"""
    try:
        return d.get(key)
    except Exception:
        return None