from __future__ import annotations
from django.db import transaction
from pokemon.models import Type
from pokemon.services.api import get_json, url


@transaction.atomic
def sync_types() -> int:
    """
    Upsert the /type index into the Type table (slug, name).
    Types are ~20, so paging is not required.

    Returns
    -------
    int
        Number of new records created.
    """
    data = get_json(url("type"))
    created = 0
    for row in data.get("results", []):
        slug = row["name"]
        _, was_created = Type.objects.update_or_create(
            slug=slug,
            defaults={"name": slug.title()},
        )
        if was_created:
            created += 1
    return created


def ensure_types() -> None:
    """
    Ensure the Type table is populated.

    If the table is empty, triggers a full sync.
    """
    if Type.objects.count() == 0:
        sync_types()