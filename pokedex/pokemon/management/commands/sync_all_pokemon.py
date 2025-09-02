from __future__ import annotations
"""
Management command: sync the entire Pokédex into the local DB cache.

Thin wrapper that:
- parses CLI args,
- wires a ProgressPrinter for live feedback,
- delegates multi-pass orchestration to `SyncRunner` (with adaptive throttling),
- prints a concise final summary.

See:
- `pokemon.orchestration.runner.SyncRunner` for orchestration.
- `pokemon.services.sync.pokemon.sync_all_pokemon` for the per-pass service.
"""

from typing import Dict
from django.core.management.base import BaseCommand

from pokemon.utils.progress import ProgressPrinter
from pokemon.orchestration.runner import SyncRunner
from pokemon.services.cache.pokemon import sync_all_pokemon


class Command(BaseCommand):
    help = "Sync ALL Pokémon into local DB cache (idempotent, multi-run with adaptive throttling)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--workers", type=int, default=2, help="Parallel workers (I/O bound).")
        parser.add_argument("--batch-size", type=int, default=100, help="Index batch size for /pokemon.")
        parser.add_argument("--sleep", type=float, default=0.1, help="Base sleep seconds between batches.")
        parser.add_argument("--refresh-all", action="store_true", help="Refresh even existing records.")
        parser.add_argument("--no-progress", action="store_true", help="Disable live progress output.")
        parser.add_argument("--quiet", action="store_true", help="Less verbose run headers.")
        parser.add_argument("--max-runs", type=int, default=5, help="Run up to N times while failures remain.")
        parser.add_argument("--target-fail", type=int, default=1, help="Stop early once failed <= target-fail.")

    def handle(self, *args, **opts) -> None:
        printer = ProgressPrinter(enabled=not opts["no_progress"])

        def progress_cb(state: Dict) -> None:
            if state.get("phase") == "index":
                printer.line(f"[index] discovered ~{state.get('total', 0)} Pokémon")
            else:
                # service already emits: {phase,total,done,synced,failed,skipped,batch,batches,rate,eta}
                printer.live(state)

        if not opts["quiet"]:
            self.stdout.write(self.style.WARNING(
                f"Starting full Pokémon sync (workers={opts['workers']}, batch-size={opts['batch_size']}, "
                f"sleep={opts['sleep']}, refresh_all={opts['refresh_all']})"
            ))

        # Generic runner configured for the Pokémon service
        runner = SyncRunner(
            run_fn=sync_all_pokemon,
            success_key="synced",               # service returns {'synced': ...}
            run_extra_kwargs={
                # forward service warnings (e.g., missing taxonomy rows) to CLI
                "logger": (lambda s: self.stdout.write(s + "\n"))
            },

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
            f"POKÉMON sync finished after {result['runs']} run(s). "
            f"total_synced={result['total_synced']} "
            f"total_skipped={result['total_skipped']} "
            f"last_failed={result['last_failed']}"
        )
        if result["last_failed"] is not None and result["last_failed"] > opts["target_fail"]:
            self.stdout.write(self.style.ERROR(summary))
        else:
            self.stdout.write(self.style.SUCCESS(summary))