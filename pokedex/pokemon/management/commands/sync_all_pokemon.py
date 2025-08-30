from __future__ import annotations
"""
Management command: Sync the entire Pokédex into the local DB cache.

This command is intentionally thin. It:
- Parses CLI arguments.
- Wires a ProgressPrinter (live CLI feedback).
- Delegates multi-run orchestration with adaptive throttling to `SyncRunner`.
- Prints a concise final summary.

See:
- `pokemon.orchestration.runner.SyncRunner` for the orchestration logic.
- `pokemon.services.sync_all.sync_all_pokemon` for the low-level sync routine
  that actually fetches Pokémon data and accepts a `progress` callback.
"""

from typing import Dict
from django.core.management.base import BaseCommand
from pokemon.utils.progress import ProgressPrinter
from pokemon.orchestration.runner import SyncRunner


class Command(BaseCommand):
    """
    Django management command entrypoint.

    Runs a multi-pass synchronization of the full Pokédex into the local DB cache.
    Each pass calls the service function `sync_all_pokemon` and reports progress
    via a callback. Between passes, the runner gently decreases parallelism and
    increases sleep to reduce transient failures on the public API.

    Typical usage:
        $ python manage.py sync_all_pokemon
        $ python manage.py sync_all_pokemon --target-fail 0
        $ python manage.py sync_all_pokemon --workers 4 --batch-size 150 --sleep 0.2

    Arguments (see `add_arguments` for details):
        --workers       Parallel HTTP workers (I/O bound).
        --batch-size    Size of index page when enumerating IDs from PokeAPI.
        --sleep         Base sleep between batches (seconds).
        --refresh-all   Refresh existing rows (not only missing).
        --no-progress   Disable live progress output (useful in CI).
        --quiet         Suppress run headers; keep final summary.
        --max-runs      Maximum number of passes while failures remain.
        --target-fail   Stop early once failures drop to this threshold.
    """

    help = "Sync ALL Pokémon into local DB cache (idempotent, multi-run with adaptive throttling)."

    def add_arguments(self, parser) -> None:
        """
        Register CLI arguments for the command.

        Notes:
            - Defaults are conservative and API-friendly.
            - Increase `--workers` and/or `--batch-size` only if the API
              remains stable; otherwise expect more transient failures.
        """
        parser.add_argument("--workers", type=int, default=2, help="Parallel workers (I/O bound).")
        parser.add_argument("--batch-size", type=int, default=100, help="Index batch size for /pokemon endpoint.")
        parser.add_argument("--sleep", type=float, default=0.1, help="Base sleep seconds between batches.")
        parser.add_argument("--refresh-all", action="store_true", help="Refresh even existing records.")
        parser.add_argument("--no-progress", action="store_true", help="Disable live progress output.")
        parser.add_argument("--quiet", action="store_true", help="Less verbose run headers.")
        parser.add_argument("--max-runs", type=int, default=5, help="Run up to N times while failures remain.")
        parser.add_argument("--target-fail", type=int, default=1, help="Stop when failed <= target-fail.")

    def handle(self, *args, **opts) -> None:
        """
        Parse arguments, wire progress printing, run the orchestrator, and
        print a final summary.

        The `progress_cb` translates service progress dictionaries into a
        single live-updating line on the terminal (unless `--no-progress`).
        """
        printer = ProgressPrinter(enabled=not opts["no_progress"])

        def progress_cb(state: Dict) -> None:
            if state.get("phase") == "index":
                printer.line(f"[index] discovered ~{state.get('total', 0)} Pokémon")
            else:
                printer.live(state)

        if not opts["quiet"]:
            self.stdout.write(self.style.WARNING(
                f"Starting full sync (workers={opts['workers']}, batch-size={opts['batch_size']}, "
                f"sleep={opts['sleep']}, refresh_all={opts['refresh_all']})"
            ))

        runner = SyncRunner(
            workers=opts["workers"],
            batch_size=opts["batch_size"],
            base_sleep=opts["sleep"],
            refresh_all=opts["refresh_all"],
            max_runs=opts["max_runs"],
            target_fail=opts["target_fail"],
            progress=progress_cb,
            logger=self.stdout if not opts["quiet"] else None,
        )

        try:
            result = runner.run()
        finally:
            printer.finalize_line()

        summary = (
            f"ALL sync finished after {result['runs']} run(s). "
            f"total_synced={result['total_synced']} "
            f"total_skipped={result['total_skipped']} "
            f"last_failed={result['last_failed']}"
        )
        if result["last_failed"] and result["last_failed"] > opts["target_fail"]:
            self.stdout.write(self.style.ERROR(summary))
        else:
            self.stdout.write(self.style.SUCCESS(summary))