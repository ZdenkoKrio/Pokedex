from django.core.management.base import BaseCommand
from pokemon.models import Type, Ability, Generation
from pokemon.services.taxonomy import (
    sync_types, sync_abilities, sync_generations
)


class Command(BaseCommand):
    help = "Idempotent refresh of taxonomies (types, abilities, generations)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-sync even if tables are already populated.",
        )
        parser.add_argument(
            "--abilities-limit",
            type=int,
            default=20000,
            help="Max number of abilities to fetch (default: 20000).",
        )

    def handle(self, *args, **kw):
        force = kw.get("force", False)
        abilities_limit = kw.get("abilities_limit", 20000)

        created_types = created_abilities = created_generations = 0

        if force or Type.objects.count() == 0:
            created_types = sync_types()

        if force or Ability.objects.count() == 0:
            created_abilities = sync_abilities(limit=abilities_limit)

        if force or Generation.objects.count() == 0:
            created_generations = sync_generations()

        self.stdout.write(self.style.SUCCESS(
            f"Taxonomies refreshed "
            f"(types +{created_types}, abilities +{created_abilities}, generations +{created_generations})."
        ))