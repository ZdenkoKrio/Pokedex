from __future__ import annotations
from django.db import transaction
from pokemon.models import Generation
from pokemon.services.api import get_json, url


@transaction.atomic
def sync_generations() -> int:
    """
    Upsert the /generation index into the Generation table (slug, name).
    Idempotent: existing rows are updated, new ones are inserted.

    Returns
    -------
    int
        Number of new records created.
    """
    data = get_json(url("generation"))
    created = 0
    for row in data.get("results", []):
        slug = row["name"]
        _, was_created = Generation.objects.update_or_create(
            slug=slug,
            defaults={"name": slug.replace("generation-", "Generation ").replace("-", " ").title()},
        )
        if was_created:
            created += 1
    return created


def ensure_generations(min_count: int = 1) -> None:
    """
    Ensure the Generation table is populated.

    If there are fewer than `min_count` rows, triggers a sync.
    """
    if Generation.objects.count() < min_count:
        sync_generations()