from __future__ import annotations
"""
Minimal bootstrap: run taxonomies → Pokémon → evolution chains with defaults.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = "Sync taxonomies, Pokémon, and evolution chains in the correct order (defaults)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--refresh-all", action="store_true",
                            help="Refresh existing rows in Pokémon/Evo passes.")
        parser.add_argument("--no-progress", action="store_true",
                            help="Disable live progress output for bulk passes.")
        parser.add_argument("--quiet", action="store_true",
                            help="Less verbose run headers for bulk passes.")

    def handle(self, *args, **opts) -> None:
        # 1) Taxonomies (defaults: only fill if empty; no special flags needed)
        try:
            if not opts["quiet"]:
                self.stdout.write(self.style.WARNING("[1/3] Syncing taxonomies…"))
            call_command("sync_taxonomies")  # uses its own defaults
            if not opts["quiet"]:
                self.stdout.write(self.style.SUCCESS("[1/3] Taxonomies OK"))
        except Exception as e:
            raise CommandError(f"Taxonomy sync failed: {e!r}") from e

        # 2) Pokémon (bulk; rely on command defaults, optionally pass flags)
        try:
            if not opts["quiet"]:
                self.stdout.write(self.style.WARNING("[2/3] Syncing Pokémon…"))
            call_command(
                "sync_all_pokemon",
                refresh_all=opts["refresh_all"],
                no_progress=opts["no_progress"],
                quiet=opts["quiet"],
            )
            if not opts["quiet"]:
                self.stdout.write(self.style.SUCCESS("[2/3] Pokémon OK"))
        except Exception as e:
            raise CommandError(f"Pokémon sync failed: {e!r}") from e

        # 3) Evolution chains (bulk; rely on command defaults, optionally pass flags)
        try:
            if not opts["quiet"]:
                self.stdout.write(self.style.WARNING("[3/3] Syncing evolution chains…"))
            call_command(
                "sync_all_evo_chains",
                refresh_all=opts["refresh_all"],
                no_progress=opts["no_progress"],
                quiet=opts["quiet"],
            )
            if not opts["quiet"]:
                self.stdout.write(self.style.SUCCESS("[3/3] Evolution chains OK"))
        except Exception as e:
            raise CommandError(f"Evolution-chain sync failed: {e!r}") from e

        if not opts["quiet"]:
            self.stdout.write(self.style.SUCCESS("All done ✅"))