#!/usr/bin/env python3
"""Run the whole pipeline twice against the local fixture server and show it.

Everything here is offline. The fixture server runs on a thread inside this
process, bound to 127.0.0.1 on a port the kernel picks, and the port is masked
in the output as ``<port>`` so the capture is byte-stable across machines.

Two runs, one database. The point of the second run is the whole day: it fetches
the same nine records, validates the same seven, and stores **none** of them,
because the idempotence key already holds them. The report is identical. The
exit code is identical. Nothing had to be cleaned up first.

    .venv/bin/python examples/demo_run.py
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fixture_server  # noqa: E402
from config import load_config  # noqa: E402
from ingest import fetch_source  # noqa: E402
from logs import RunLogger, fixed_clock, redact  # noqa: E402
from pipeline import run_pipeline  # noqa: E402

TOKEN = "demo-token-value"
REPORT_AT = "2026-08-16T12:00:00Z"


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def mask(text: str, port: int) -> str:
    return text.replace(f"127.0.0.1:{port}", "127.0.0.1:<port>")


def main() -> int:
    server, port = fixture_server.start_background_server(token=TOKEN)
    base_url = f"http://127.0.0.1:{port}"
    workdir = Path(tempfile.mkdtemp(prefix="day098-"))
    # Work inside the temporary directory so database_url can stay at its
    # default, relative value. Nothing this script prints is then a path that
    # exists only on the machine that ran it.
    origin = Path.cwd()
    os.chdir(workdir)

    environ = {
        "PIPELINE_BASE_URL": base_url,
        "PIPELINE_API_TOKEN": TOKEN,
        "PIPELINE_RETRY_BACKOFF_SECONDS": "0.01",
    }
    overrides = {"report_at": REPORT_AT, "window_hours": 12, "sources": "alpha,bravo,charlie"}
    config = load_config(environ=environ, overrides=overrides)
    # The same resolution with the port replaced by a fixed marker, purely so the
    # printed table is identical on every machine. Only base_url differs.
    display_config = load_config(
        environ={**environ, "PIPELINE_BASE_URL": "http://127.0.0.1:<port>"},
        overrides=overrides,
    )

    print("Day 098 — the whole pipeline, twice")
    print("=" * 36)
    print("fixture server : http://127.0.0.1:<port> (the kernel chose the port)")
    print("database       : a fresh file in a temporary directory")
    print(f"report instant : {REPORT_AT} (a parameter, not the clock)")

    rule("1. Configuration, and where every value came from")
    print(display_config.provenance_table())
    print()
    print("api_token is set and is never printed. That is the point of marking it.")

    outcomes = []
    for number, run_id in enumerate(("run-000000000001", "run-000000000002"), start=1):
        rule(f"{number + 1}. Run {number} — run id {run_id}")
        log_stream = io.StringIO()
        out_stream = io.StringIO()
        logger = RunLogger(
            run_id,
            stream=log_stream,
            clock=fixed_clock(),
            level=str(config["log_level"]),
            secrets=config.secrets,
        )
        outcome = run_pipeline(
            config,
            run_id=run_id,
            logger=logger,
            out=out_stream,
            sleep=lambda _seconds: None,
            started_at=REPORT_AT,
        )
        outcomes.append(outcome)

        print("structured log (stderr), one JSON object per line:")
        for line in log_stream.getvalue().splitlines():
            print(("  " + mask(line, port)).rstrip())
        print()
        print("report (stdout):")
        for line in out_stream.getvalue().splitlines():
            print(("  " + line).rstrip())
        print()
        print(f"exit code: {outcome.exit_code}  ({outcome.status})")

    rule("4. What the second run proves")
    first, second = outcomes
    print(f"  records fetched      run 1: {first.fetched:>2}    run 2: {second.fetched:>2}")
    print(f"  records accepted     run 1: {first.accepted:>2}    run 2: {second.accepted:>2}")
    print(f"  records rejected     run 1: {first.rejected:>2}    run 2: {second.rejected:>2}")
    print(f"  rows inserted        run 1: {first.inserted:>2}    run 2: {second.inserted:>2}")
    print(f"  duplicates skipped   run 1: {first.duplicates:>2}    run 2: {second.duplicates:>2}")
    print(f"  rows in the store    run 1: {first.total_rows:>2}    run 2: {second.total_rows:>2}")
    print(f"  reports identical    {first.report_text == second.report_text}")
    print(f"  exit codes identical {first.exit_code == second.exit_code}")
    print()
    print("  The pipeline was run twice and the data was stored once. Every failure")
    print("  in this design now has the same remedy: run it again.")

    rule("5. Retry only what is worth retrying")
    fixture_server.reset_flaky_counter()
    for source, note in (("bravo", "500 twice, then 200"), ("delta", "404, and it will stay 404")):
        result = fetch_source(
            base_url,
            source,
            token=TOKEN,
            timeout=2.0,
            attempts=3,
            backoff=0.0,
            sleep=lambda _seconds: None,
        )
        print(
            f"  {source:<8} attempts={result.attempts}  ok={result.ok}  "
            f"status={result.status}  ({note})"
        )
    print()
    print("  bravo was worth three attempts. delta was worth one. The difference is")
    print("  whether the status code describes a moment or a mistake.")

    rule("6. The secret, and the upstream that echoed it back")
    leaky = fetch_source(
        base_url, "charlie", token=TOKEN, timeout=2.0, attempts=1, backoff=0.0
    )
    print(f"  raw error body from charlie : {leaky.error}")
    print(f"  after the log redactor      : {redact(leaky.error, config.secrets)}")
    print()
    print("  Nobody wrote code to log the token. The upstream service put it in an")
    print("  error message, and the error message went to the log. Redaction has to")
    print("  live in the logger, where it cannot be forgotten.")

    rule("7. Every log line carries the run id")
    log_stream = io.StringIO()
    logger = RunLogger("run-000000000003", stream=log_stream, clock=fixed_clock(), secrets=config.secrets)
    run_pipeline(
        config,
        run_id="run-000000000003",
        logger=logger,
        out=io.StringIO(),
        sleep=lambda _seconds: None,
        started_at=REPORT_AT,
    )
    records = [json.loads(line) for line in log_stream.getvalue().splitlines()]
    stages = [record["event"] for record in records if record["event"].startswith("stage.")]
    print(f"  log lines          : {len(records)}")
    print(f"  stage summaries    : {len(stages)} -> {', '.join(stages)}")
    print(f"  distinct run ids   : {sorted({record['run_id'] for record in records})}")

    server.shutdown()
    server.server_close()
    os.chdir(origin)
    for path in sorted(workdir.iterdir()):
        path.unlink()
    workdir.rmdir()
    print()
    print(f"temporary database removed: {not workdir.exists()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
