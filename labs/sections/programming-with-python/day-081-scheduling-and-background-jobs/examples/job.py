"""The command a scheduler would run — and the command you run by hand today.

Two subcommands, in the argparse style of Day 80:

    python3 examples/job.py run   --output-dir /tmp/reports
    python3 examples/job.py watch --heartbeat-file /tmp/reports/heartbeat.json

``run`` is the job. ``watch`` is the dead man's switch that notices when
``run`` has quietly stopped happening. They are separate programs on purpose:
a watchdog that lives inside the job it watches cannot report that the job did
not start.

``--now`` injects the clock. It exists so that every time-dependent behaviour
in this lab — "which day's report is this?", "is the heartbeat stale?", "what
happens at 02:30 on the day the clocks change?" — can be exercised in a
fraction of a second instead of waited for. That is Day 74's boundary lesson
applied to the one boundary that scheduling is entirely made of.

Exit codes:
    0    the work is done, or was already done
    1    the work raised
    75   another copy holds the lock; nothing was done  (sysexits EX_TEMPFAIL)
    124  the work exceeded its timeout and was interrupted  (as GNU timeout does)
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
from pathlib import Path

from clock import Clock, frozen_clock, system_clock
from reportjob import generate_daily_report
from runner import (
    EXIT_MEANINGS,
    EXIT_OK,
    combined_logger,
    jsonl_logger,
    run_job,
    stream_logger,
)
from watchdog import check_heartbeat

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "data" / "readings.csv"


def build_clock(now: str | None, tz: str) -> Clock:
    if now is None:
        return system_clock(tz)
    moment = dt.datetime.fromisoformat(now)
    if moment.tzinfo is None:
        raise SystemExit(
            "--now needs a timezone offset, for example 2026-07-20T02:30:00+00:00. "
            "A naive timestamp means 'whatever this machine thinks local time is', "
            "which is the bug this lab is about."
        )
    return frozen_clock(moment)


def command_run(args: argparse.Namespace) -> int:
    clock = build_clock(args.now, args.timezone)
    output_dir = Path(args.output_dir)
    report_date = (
        dt.date.fromisoformat(args.date)
        if args.date
        else (clock().date() - dt.timedelta(days=1))
    )

    def work() -> dict[str, object]:
        if args.simulate_hang:
            time.sleep(args.simulate_hang)
        if args.simulate_failure:
            raise RuntimeError("the upstream feed returned nothing (simulated)")
        status, path = generate_daily_report(
            source=Path(args.data),
            output_dir=output_dir,
            report_date=report_date,
            generated_at=clock(),
        )
        return {
            "status": "ok" if status == "written" else "skipped",
            "report_date": report_date.isoformat(),
            "output": str(path),
            "action": status,
        }

    loggers = [stream_logger()]
    if args.log_file:
        loggers.append(jsonl_logger(args.log_file))

    run = run_job(
        name=args.name,
        work=work,
        clock=clock,
        lock_path=args.lock_file or (output_dir / f"{args.name}.lock"),
        log=combined_logger(*loggers),
        timeout_seconds=args.timeout,
        heartbeat_path=args.heartbeat_file
        or (output_dir / f"{args.name}.heartbeat.json"),
    )
    if run.exit_code != EXIT_OK:
        print(
            f"{args.name}: {run.status} -> exit {run.exit_code} "
            f"({EXIT_MEANINGS[run.exit_code]})",
            file=sys.stderr,
        )
    return run.exit_code


def command_watch(args: argparse.Namespace) -> int:
    clock = build_clock(args.now, args.timezone)
    verdict = check_heartbeat(
        heartbeat_path=args.heartbeat_file,
        clock=clock,
        max_age=dt.timedelta(minutes=args.max_age_minutes),
    )
    print(f"{verdict.state.upper()}: {verdict.message}")
    return 1 if verdict.alerting else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="job.py",
        description="A scheduled daily report, and the watchdog that notices when it stops.",
        epilog="This program never installs itself into any scheduler. See gen_schedules.py.",
    )
    parser.add_argument("--now", help="freeze the clock, e.g. 2026-07-20T02:30:00+00:00")
    parser.add_argument("--timezone", default="UTC", help="zone for the real clock (default UTC)")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="generate one daily report, idempotently")
    run_parser.add_argument("--output-dir", required=True, type=Path)
    run_parser.add_argument("--data", default=str(DEFAULT_DATA), help="the readings CSV")
    run_parser.add_argument("--date", help="report date (default: the day before --now)")
    run_parser.add_argument("--name", default="daily-report", help="job name used in logs and locks")
    run_parser.add_argument("--lock-file", type=Path)
    run_parser.add_argument("--log-file", type=Path, help="append JSON lines here as well")
    run_parser.add_argument("--heartbeat-file", type=Path)
    run_parser.add_argument("--timeout", type=float, default=60.0, help="seconds (0 disables)")
    run_parser.add_argument(
        "--simulate-hang", type=float, default=0.0, help="sleep this long inside the work"
    )
    run_parser.add_argument(
        "--simulate-failure", action="store_true", help="raise inside the work"
    )
    run_parser.set_defaults(func=command_run)

    watch_parser = sub.add_parser("watch", help="alert if the last success is too old")
    watch_parser.add_argument("--heartbeat-file", required=True, type=Path)
    watch_parser.add_argument("--max-age-minutes", type=float, default=2880.0)
    watch_parser.set_defaults(func=command_watch)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "timeout", None) == 0:
        args.timeout = None
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
