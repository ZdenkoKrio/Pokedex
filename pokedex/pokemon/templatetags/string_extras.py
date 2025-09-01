from django import template
register = template.Library()


@register.filter(name="replace")
def replace(value: str, args: str) -> str:
    """
    Usage: {{ value|replace:"from,to" }}
    """
    if not isinstance(value, str):
        value = str(value)

    try:
        old, new = args.split(",", 1)
    except ValueError:
        return value

    return value.replace(old, new)