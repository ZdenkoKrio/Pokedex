from .selectors import user_favorite_ids


def favorites_context(request):
    ids = user_favorite_ids(getattr(request, "user", None))
    return {"fav_count": len(ids), "fav_ids": ids}