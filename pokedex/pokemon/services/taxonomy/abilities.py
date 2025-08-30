from __future__ import annotations
from django.db import transaction
from pokemon.models import Ability
from pokemon.services.api import get_json, url


@transaction.atomic
def sync_abilities(limit: int = 20000) -> int:
    """
    Upsert the /ability index into the Ability table (slug, name).
    Uses a high limit to avoid paging.

    Parameters
    ----------
    limit : int
        Maximum number of abilities to fetch (default: 20000).

    Returns
    -------
    int
        Number of new records created.
    """
    data = get_json(url("ability") + f"?limit={limit}")
    created = 0
    for row in data.get("results", []):
        slug = row["name"]
        _, was_created = Ability.objects.update_or_create(
            slug=slug,
            defaults={"name": slug.replace("-", " ").title()},
        )
        if was_created:
            created += 1
    return created


def ensure_abilities(min_count: int = 50) -> None:
    """
    Ensure the Ability table is sufficiently populated.

    If there are fewer than `min_count` rows, triggers a sync.
    """
    if Ability.objects.count() < min_count:
        sync_abilities()