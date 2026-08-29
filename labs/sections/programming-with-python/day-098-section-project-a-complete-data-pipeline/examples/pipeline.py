"""The pipeline: five stages, one run id, and an exit code a scheduler can act on.

This is the only module that knows about all five stages, and it is deliberately
thin. Each stage has already made its own promise; this file's job is to thread
one run id through them, decide what the combination of outcomes *means*, and
say so in a way a scheduler can act on without reading English.

**The exit code is the interface to the scheduler** (Day 81). ``cron`` and
``launchd`` and every CI runner ever written know exactly one thing about your
program: the number it returned. So:

    0   success        every source answered, every record was accepted
    3   partial        the run completed and stored what it could, but at least
                       one source failed permanently or at least one record was
                       rejected. Somebody should look; nothing is on fire.
    1   failure        the run could not do its job at all — no source answered,
                       or the store refused. Page someone.

Collapsing 3 into 0 is the mistake that lets a source go dark for a month.
Collapsing 3 into 1 is the mistake that trains everyone to ignore the alert.

**Where concurrency belongs** (Day 96). Ingest is waiting work: three sources
fetched one after another spend almost all their wall-clock time blocked on a
socket, and running them concurrently is close to free. Validation is not — at
this size it is microseconds of CPU, and a thread pool would cost more in
coordination than it saves. The store is a single SQLite writer by design; two
concurrent writers buy contention, not speed. This module keeps the fetch
sequential because the lab has three sources and determinism is worth more than
milliseconds here, and says so plainly rather than pretending the choice was
forced.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import TextIO

from sqlalchemy.orm import Session

import report as report_module
from config import Config, load_config
from ingest import fetch_all
from logs import RunLogger, fixed_clock, utc_clock
from store import build_engine, record_run, store_readings, utc_text
from validate import validate_all

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_PARTIAL = 3


@dataclass
class RunOutcome:
    run_id: str
    status: str
    exit_code: int
    fetched: int
    accepted: int
    rejected: int
    inserted: int
    duplicates: int
    total_rows: int
    failed_sources: tuple[str, ...]
    report_text: str


def run_pipeline(
    config: Config,
    *,
    run_id: str,
    logger: RunLogger,
    out: TextIO,
    sleep: Callable[[float], None] | None = None,
    started_at: str | None = None,
) -> RunOutcome:
    """Run all five stages once. Returns the outcome; never raises for data."""
    sources = config.source_names
    started_at = started_at or utc_text()
    logger.event(
        "run.start",
        sources=sources,
        window_hours=config["window_hours"],
        report_at=str(config["report_at"]) or "<now>",
        database_url=str(config["database_url"]),
    )

    # ---- Stage 1: ingest -------------------------------------------------
    kwargs = {} if sleep is None else {"sleep": sleep}
    results = fetch_all(
        str(config["base_url"]),
        sources,
        token=str(config["api_token"]),
        timeout=float(config["timeout_seconds"]),  # type: ignore[arg-type]
        attempts=int(config["retry_attempts"]),  # type: ignore[arg-type]
        backoff=float(config["retry_backoff_seconds"]),  # type: ignore[arg-type]
        **kwargs,
    )
    for result in results:
        if not result.ok:
            logger.event(
                "ingest.source_failed",
                level="warning",
                source=result.source,
                attempts=result.attempts,
                status=result.status,
                error=result.error,
            )
        elif result.retried:
            logger.event(
                "ingest.source_recovered",
                source=result.source,
                attempts=result.attempts,
            )

    fetched = {result.source: result.records for result in results if result.ok}
    failed = tuple(result.source for result in results if not result.ok)
    records_fetched = sum(len(records) for records in fetched.values())
    logger.event(
        "stage.ingest",
        sources_ok=len(fetched),
        sources_failed=len(failed),
        failed_sources=list(failed),
        records_fetched=records_fetched,
        attempts_total=sum(result.attempts for result in results),
    )

    if not fetched:
        logger.event("run.end", level="error", status="failure", exit_code=EXIT_FAILURE)
        return RunOutcome(
            run_id=run_id,
            status="failure",
            exit_code=EXIT_FAILURE,
            fetched=0,
            accepted=0,
            rejected=0,
            inserted=0,
            duplicates=0,
            total_rows=0,
            failed_sources=failed,
            report_text="",
        )

    # ---- Stage 2: validate ----------------------------------------------
    outcome = validate_all(fetched)
    for rejection in outcome.rejected:
        logger.event(
            "validate.rejected",
            level="warning",
            source=rejection.source,
            index=rejection.index,
            reading_id=rejection.reading_id,
            problems=list(rejection.problems),
        )
    logger.event(
        "stage.validate",
        records_in=outcome.considered,
        accepted=len(outcome.accepted),
        rejected=len(outcome.rejected),
        reasons=outcome.reasons(),
    )

    # ---- Stage 3: store --------------------------------------------------
    engine = build_engine(str(config["database_url"]))
    with Session(engine) as session:
        stored = store_readings(session, outcome.accepted, run_id=run_id)
        logger.event(
            "stage.store",
            considered=stored.considered,
            inserted=stored.inserted,
            duplicates_skipped=stored.duplicates,
            total_rows=stored.total_rows,
        )

        # ---- Stage 4: report ---------------------------------------------
        report_at = str(config["report_at"]) or utc_text()
        built = report_module.build_report(
            session,
            report_at=report_at,
            window_hours=int(config["window_hours"]),  # type: ignore[arg-type]
            stations=sources,
        )
        report_text = report_module.format_report(built)
        out.write(report_text + "\n")
        logger.event(
            "stage.report",
            report_at=built.report_at,
            window_start=built.window_start,
            readings_in_window=built.readings_in_window,
            stations=len(built.stations),
            suspect_readings=len(built.suspect),
        )

        # ---- Stage 5: observe --------------------------------------------
        if failed or outcome.rejected:
            status, code = "partial_success", EXIT_PARTIAL
        else:
            status, code = "success", EXIT_SUCCESS

        logger.event(
            "stage.observe",
            status=status,
            exit_code=code,
            run_row=run_id,
            log_lines_so_far=len(logger.emitted) + 1,
        )
        record_run(
            session,
            run_id=run_id,
            started_at=started_at,
            status=status,
            fetched=records_fetched,
            accepted=len(outcome.accepted),
            rejected=len(outcome.rejected),
            inserted=stored.inserted,
            duplicates=stored.duplicates,
        )

    engine.dispose()
    logger.event(
        "run.end",
        level="warning" if code == EXIT_PARTIAL else "info",
        status=status,
        exit_code=code,
        stored_total=stored.total_rows,
    )
    return RunOutcome(
        run_id=run_id,
        status=status,
        exit_code=code,
        fetched=records_fetched,
        accepted=len(outcome.accepted),
        rejected=len(outcome.rejected),
        inserted=stored.inserted,
        duplicates=stored.duplicates,
        total_rows=stored.total_rows,
        failed_sources=failed,
        report_text=report_text,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Fetch station readings, validate them, store them once, and report.",
    )
    parser.add_argument("--config-file", default=None, help="TOML file, layer 2 of 4")
    parser.add_argument("--base-url", default=None, help="where the station API lives")
    parser.add_argument("--sources", default=None, help="comma-separated station names")
    parser.add_argument("--database-url", default=None, help="SQLAlchemy URL")
    parser.add_argument("--window-hours", default=None, help="report window, in hours")
    parser.add_argument("--report-at", default=None, help="report instant, ISO 8601 with offset")
    parser.add_argument("--timeout-seconds", default=None, help="per-request deadline")
    parser.add_argument("--retry-attempts", default=None, help="attempts per source")
    parser.add_argument(
        "--log-level", default=None, choices=["debug", "info", "warning", "error"]
    )
    parser.add_argument("--run-id", default=None, help="use this run id instead of a fresh one")
    parser.add_argument(
        "--explain-config",
        action="store_true",
        help="print every setting, its value and which layer set it, then exit 0",
    )
    parser.add_argument(
        "--fixed-clock",
        action="store_true",
        help="log timestamps from a fixed clock, so output is byte-comparable",
    )
    return parser


def main(argv: list[str] | None = None, *, out: TextIO | None = None, err: TextIO | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    out = out if out is not None else sys.stdout
    err = err if err is not None else sys.stderr

    overrides = {
        "base_url": args.base_url,
        "sources": args.sources,
        "database_url": args.database_url,
        "window_hours": args.window_hours,
        "report_at": args.report_at,
        "timeout_seconds": args.timeout_seconds,
        "retry_attempts": args.retry_attempts,
        "log_level": args.log_level,
    }
    try:
        config = load_config(config_file=args.config_file, overrides=overrides)
    except FileNotFoundError as exc:
        err.write(f"configuration error: {exc}\n")
        return EXIT_FAILURE

    if args.explain_config:
        out.write(config.provenance_table() + "\n")
        return EXIT_SUCCESS

    run_id = args.run_id or uuid.uuid4().hex[:12]
    logger = RunLogger(
        run_id,
        stream=err,
        clock=fixed_clock() if args.fixed_clock else utc_clock,
        level=str(config["log_level"]),
        secrets=config.secrets,
    )
    outcome = run_pipeline(config, run_id=run_id, logger=logger, out=out)
    return outcome.exit_code


if __name__ == "__main__":
    sys.exit(main())
