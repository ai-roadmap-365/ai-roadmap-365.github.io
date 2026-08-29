"""The whole day in one run, in eight parts and under a second.

    python3 examples/demo.py

Nothing here waits, nothing here schedules anything, and nothing here is left
running afterwards. Every duration you see was computed against an injected
clock.
"""

from __future__ import annotations

import datetime as dt
import json
import tempfile
from pathlib import Path

from clock import frozen_clock, ticking_clock
from cronexpr import parse
from gen_schedules import JobSchedule
from inprocess import deadline_corrected_loop, naive_sleep_loop, run_sched_schedule
from joblock import AlreadyRunning, job_lock
from reportjob import generate_daily_report
from runner import EXIT_MEANINGS, jsonl_logger, run_job
from timezones import classify_wall_time, daily_instants_local, gaps_between
from watchdog import check_heartbeat

UTC = dt.timezone.utc
HERE = Path(__file__).resolve().parent
NOW = dt.datetime(2026, 7, 20, 2, 30, tzinfo=UTC)
DAY = dt.date(2026, 7, 19)


def heading(number: int, text: str) -> None:
    print()
    print(f"{number}. {text}")
    print("=" * (len(text) + 3))


def main() -> int:
    heading(1, "A sleep loop drifts, and the drift never stops growing")
    naive = naive_sleep_loop(runs=100, interval=60, work_seconds=5)
    fixed = deadline_corrected_loop(runs=100, interval=60, work_seconds=5)
    print("  work(); sleep(60) with 5s of work")
    print(f"      gap between runs : {naive.starts[1] - naive.starts[0]:.0f}s (you wrote 60)")
    print(f"      run 100 is late by: {naive.final_drift:.0f}s")
    print("  sleep until the next deadline instead")
    print(f"      gap between runs : {fixed.starts[1] - fixed.starts[0]:.0f}s")
    print(f"      run 100 is late by: {fixed.final_drift:.0f}s")

    heading(2, "sched with an injected clock: six hours of schedule, no waiting")
    fired, fake = run_sched_schedule(delays=[3600, 7200, 21600])
    for when, index in fired:
        print(f"      event {index} fired at t+{when:.0f}s")
    print(f"      total time 'waited': {fake.total_slept:.0f}s of fake time, 0s of real time")

    with tempfile.TemporaryDirectory(prefix="day081-demo.") as workdir:
        out = Path(workdir)

        heading(3, "Idempotence: run it twice, get one report")
        for attempt in (1, 2):
            status, path = generate_daily_report(
                source=HERE / "data" / "readings.csv",
                output_dir=out,
                report_date=DAY,
                generated_at=NOW,
            )
            print(f"      run {attempt}: {status:8s} -> {path.name}")
        files = sorted(p.name for p in out.glob("report-*.json"))
        print(f"      files on disk: {files}")
        payload = json.loads((out / f"report-{DAY.isoformat()}.json").read_text())
        print(f"      readings summarised: {payload['reading_count']}")

        heading(4, "The lock: a second run refuses rather than doubling the work")
        lock = out / "daily-report.lock"
        did_work: list[str] = []
        with job_lock(lock):
            run = run_job(
                name="daily-report",
                work=lambda: did_work.append("worked") or {},
                clock=frozen_clock(NOW),
                lock_path=lock,
                log=lambda event: None,
            )
        print(f"      status   : {run.status}")
        print(f"      exit code: {run.exit_code}  ({EXIT_MEANINGS[run.exit_code]})")
        print(f"      work done: {bool(did_work)}")
        try:
            with job_lock(lock):
                print("      lock is free again once the holder finished: yes")
        except AlreadyRunning:
            print("      lock is free again once the holder finished: no")

        heading(5, "A hung job hits its timeout instead of blocking every later run")
        import time

        started = time.monotonic()
        hung = run_job(
            name="daily-report",
            work=lambda: time.sleep(30),
            clock=ticking_clock(NOW, dt.timedelta(seconds=30)),
            lock_path=out / "hang.lock",
            log=jsonl_logger(out / "job.log"),
            timeout_seconds=0.2,
        )
        print("      the work asked for 30s, the budget was 0.2s")
        print(f"      status   : {hung.status}")
        print(f"      exit code: {hung.exit_code}  ({EXIT_MEANINGS[hung.exit_code]})")
        print(f"      real time spent: {time.monotonic() - started:.2f}s")
        print("      log line:")
        print("        " + (out / "job.log").read_text().strip())

        heading(6, "The dead man's switch: alerting on silence, not on failure")
        heartbeat = out / "heartbeat.json"
        heartbeat.write_text(
            json.dumps({"job": "daily-report", "last_success": (NOW - dt.timedelta(hours=6)).isoformat()})
        )
        for label, moment in (
            ("six hours ago", NOW),
            ("two days later, nothing has run", NOW + dt.timedelta(days=2)),
        ):
            verdict = check_heartbeat(
                heartbeat_path=heartbeat,
                clock=frozen_clock(moment),
                max_age=dt.timedelta(hours=26),
            )
            print(f"      {label}:")
            print(f"        {verdict.state.upper()}: {verdict.message}")

    heading(7, "Time zones: the two mornings a local schedule is wrong")
    for naive_time in (dt.datetime(2026, 3, 8, 2, 30), dt.datetime(2026, 11, 1, 1, 30)):
        verdict = classify_wall_time(naive_time, "America/New_York")
        print(f"      {verdict.wall_time} America/New_York -> {verdict.kind}")
        print(f"        {verdict.note}")
    spring = gaps_between(
        daily_instants_local(
            start_date=dt.date(2026, 3, 6), days=5, hour=12, minute=0,
            zone_name="America/New_York",
        )
    )
    utc_gaps = gaps_between(
        daily_instants_local(
            start_date=dt.date(2026, 3, 6), days=5, hour=12, minute=0, zone_name="UTC"
        )
    )
    print(f"      hours between daily 12:00 runs, local: {spring}")
    print(f"      hours between daily 12:00 runs, UTC  : {utc_gaps}")

    heading(8, "One schedule, three dialects — generated, not installed")
    schedule = JobSchedule(label="com.example.dailyreport", minute=30, hour=2)
    print("      cron    : " + schedule.cron_expression)
    print("      launchd : StartCalendarInterval Hour=2 Minute=30")
    print("      systemd : OnCalendar=" + schedule.on_calendar)
    print("      reads as: " + parse(schedule.cron_expression).describe())
    print()
    print("      Nothing was scheduled. No crontab, no launchd job, no systemd timer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
