from __future__ import annotations
"""
Management command: sync ALL evolution chains into the local DB.

Thin wrapper that:
- parses CLI args,
- wires a ProgressPrinter for live feedback,
- delegates multi-pass orchestration to `SyncRunner`,
- treats the service's "ok" metric as "synced" in the runner summary.
"""

from typing import Dict
from django.core.management.base import BaseCommand

from pokemon.utils.progress import ProgressPrinter
from pokemon.orchestration.runner import SyncRunner
from pokemon.services.sync.evo import sync_all_evo_chains


class Command(BaseCommand):
    help = "Sync ALL evolution chains (and backfill PokemonCache.evolution_chain_id if present)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--workers", type=int, default=1, help="Parallel workers (I/O bound).")
        parser.add_argument("--batch-size", type=int, default=100, help="Index batch size for /evolution-chain.")
        parser.add_argument("--sleep", type=float, default=0.1, help="Base sleep seconds between batches.")
        parser.add_argument("--refresh-all", action="store_true", help="Refresh even existing chain rows.")
        parser.add_argument("--no-progress", action="store_true", help="Disable live progress output.")
        parser.add_argument("--quiet", action="store_true", help="Less verbose run headers.")
        parser.add_argument("--max-runs", type=int, default=3, help="Run up to N times while failures remain.")
        parser.add_argument("--target-fail", type=int, default=0, help="Stop early once failed <= target-fail.")

    def handle(self, *args, **opts) -> None:
        printer = ProgressPrinter(enabled=not opts["no_progress"])

        def progress_cb(state: Dict) -> None:
            # evo service emits {phase,total,done,ok,failed,skipped,batch,batches,rate,eta}
            if state.get("phase") == "index":
                printer.line(f"[index] discovered ~{state.get('total', 0)} evolution chains")
            else:
                # map ok → synced for the shared printer format
                printer.live({
                    "phase": state.get("phase"),
                    "total": state.get("total", 0),
                    "done": state.get("done", 0),
                    "synced": state.get("ok", 0),
                    "failed": state.get("failed", 0),
                    "skipped": state.get("skipped", 0),
                    "batch": state.get("batch", 0),
                    "batches": state.get("batches", 0),
                    "rate": state.get("rate", 0.0),
                    "eta": state.get("eta", 0.0),
                })

        if not opts["quiet"]:
            self.stdout.write(self.style.WARNING(
                f"Starting evo-chain sync (workers={opts['workers']}, batch-size={opts['batch_size']}, "
                f"sleep={opts['sleep']}, refresh_all={opts['refresh_all']})"
            ))

        runner = SyncRunner(
            run_fn=sync_all_evo_chains,         # concrete pass function
            success_key="ok",                   # evo service returns {'ok': ...}

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
            f"EVO sync finished after {result['runs']} run(s). "
            f"total_ok={result['total_synced']} "
            f"total_skipped={result['total_skipped']} "
            f"last_failed={result['last_failed']}"
        )
        if result["last_failed"] is not None and result["last_failed"] > opts["target_fail"]:
            self.stdout.write(self.style.ERROR(summary))
        else:
            self.stdout.write(self.style.SUCCESS(summary))