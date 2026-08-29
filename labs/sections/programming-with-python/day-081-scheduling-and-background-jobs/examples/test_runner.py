"""The operational properties: idempotence, locking, timeout, logging, heartbeat.

Every test here injects the clock, so a run that "takes a second" or a
heartbeat that is "two days old" costs nothing at all.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest
from clock import frozen_clock, ticking_clock
from joblock import AlreadyRunning, job_lock
from reportjob import (
    already_written,
    build_report,
    generate_daily_report,
    load_readings,
    report_path,
)
from runner import (
    EXIT_ALREADY_RUNNING,
    EXIT_FAILED,
    EXIT_OK,
    EXIT_TIMEOUT,
    JobTimeout,
    jsonl_logger,
    run_job,
)

UTC = dt.timezone.utc
NOW = dt.datetime(2026, 7, 20, 2, 30, tzinfo=UTC)
DAY = dt.date(2026, 7, 19)
DATA = Path(__file__).resolve().parent / "data" / "readings.csv"


@pytest.fixture
def collected():
    events: list[dict] = []
    return events, events.append


# --------------------------------------------------------------------------
# The work itself
# --------------------------------------------------------------------------


def test_the_report_summarises_only_the_requested_day():
    readings = load_readings(DATA, DAY)
    assert sorted(readings) == ["ALPHA", "BRAVO", "CHARLIE"]
    report = build_report(readings, report_date=DAY, generated_at=NOW)
    assert report.reading_count == 6
    alpha = next(s for s in report.stations if s.station == "ALPHA")
    assert alpha.count == 3
    assert alpha.minimum == 16.8
    assert alpha.maximum == 19.6
    assert round(alpha.mean, 4) == round((16.8 + 18.0 + 19.6) / 3, 4)


def test_running_the_job_twice_leaves_exactly_one_report(tmp_path):
    """Idempotence: the property that makes retries and catch-up runs safe."""
    first = generate_daily_report(
        source=DATA, output_dir=tmp_path, report_date=DAY, generated_at=NOW
    )
    second = generate_daily_report(
        source=DATA,
        output_dir=tmp_path,
        report_date=DAY,
        generated_at=NOW + dt.timedelta(hours=1),
    )
    assert first[0] == "written"
    assert second[0] == "skipped"
    assert first[1] == second[1]
    assert sorted(p.name for p in tmp_path.iterdir()) == [f"report-{DAY.isoformat()}.json"]
    payload = json.loads(first[1].read_text())
    assert payload["reading_count"] == 6
    # The second run did not rewrite the file: the timestamp is the first run's.
    assert payload["generated_at"] == NOW.isoformat()


def test_a_truncated_output_file_is_not_mistaken_for_a_finished_run(tmp_path):
    """A crash mid-write must produce a retry, not a permanent silent skip."""
    partial = report_path(tmp_path, DAY)
    partial.write_text('{"report_date": "2026-07-19", "stat')
    assert already_written(tmp_path, DAY) is False
    status, path = generate_daily_report(
        source=DATA, output_dir=tmp_path, report_date=DAY, generated_at=NOW
    )
    assert status == "written"
    assert json.loads(path.read_text())["reading_count"] == 6


def test_no_partial_files_are_left_behind(tmp_path):
    generate_daily_report(
        source=DATA, output_dir=tmp_path, report_date=DAY, generated_at=NOW
    )
    assert [p.name for p in tmp_path.iterdir() if p.name.endswith(".partial")] == []


# --------------------------------------------------------------------------
# The lock
# --------------------------------------------------------------------------


def test_the_lock_is_exclusive_within_one_process(tmp_path):
    path = tmp_path / "job.lock"
    with job_lock(path):
        with pytest.raises(AlreadyRunning):
            with job_lock(path):
                pytest.fail("the second acquisition should have been refused")


def test_the_lock_is_released_even_when_the_work_raises(tmp_path):
    path = tmp_path / "job.lock"
    with pytest.raises(ValueError):
        with job_lock(path):
            raise ValueError("boom")
    with job_lock(path):  # must not raise
        pass


def test_a_second_run_under_a_held_lock_exits_75_and_does_no_work(tmp_path, collected):
    events, log = collected
    path = tmp_path / "job.lock"
    calls = []

    with job_lock(path):
        run = run_job(
            name="daily-report",
            work=lambda: calls.append("worked") or {},
            clock=frozen_clock(NOW),
            lock_path=path,
            log=log,
        )
    assert run.exit_code == EXIT_ALREADY_RUNNING
    assert run.status == "already-running"
    assert calls == []  # the work never ran — this is the assertion that matters
    assert events[-1]["status"] == "already-running"


# --------------------------------------------------------------------------
# The runner: statuses, exit codes, timeout, logs, heartbeat
# --------------------------------------------------------------------------


def test_a_successful_run_exits_zero_and_logs_one_line(tmp_path, collected):
    events, log = collected
    run = run_job(
        name="daily-report",
        work=lambda: {"rows": 6},
        clock=ticking_clock(NOW, dt.timedelta(seconds=2)),
        lock_path=tmp_path / "job.lock",
        log=log,
    )
    assert run.exit_code == EXIT_OK
    assert run.status == "ok"
    assert run.duration_seconds == 2.0
    assert len(events) == 1
    assert events[0]["run_id"] == "daily-report-20260720T023000+0000"
    assert events[0]["rows"] == 6


def test_a_failing_run_exits_one_and_names_the_exception(tmp_path, collected):
    events, log = collected

    def work():
        raise RuntimeError("the upstream feed returned nothing")

    run = run_job(
        name="daily-report",
        work=work,
        clock=frozen_clock(NOW),
        lock_path=tmp_path / "job.lock",
        log=log,
    )
    assert run.exit_code == EXIT_FAILED
    assert events[0]["error"] == "RuntimeError"
    assert "upstream feed" in events[0]["message"]


def test_a_hung_job_is_interrupted_by_the_timeout(tmp_path, collected):
    """A real hang, killed by a real SIGALRM — the only test here that waits.

    It waits for 0.2 seconds, not for the 30 the job asks for, which is the
    whole point of having a timeout at all.
    """
    import time

    events, log = collected
    started = time.monotonic()
    run = run_job(
        name="daily-report",
        work=lambda: time.sleep(30),
        clock=frozen_clock(NOW),
        lock_path=tmp_path / "job.lock",
        log=log,
        timeout_seconds=0.2,
    )
    elapsed = time.monotonic() - started
    assert run.exit_code == EXIT_TIMEOUT
    assert run.status == "timeout"
    assert elapsed < 5, f"the timeout did not fire; the test waited {elapsed:.1f}s"
    assert events[0]["error"] == "JobTimeout"


def test_the_timeout_releases_the_lock_so_the_next_run_can_start(tmp_path, collected):
    import time

    events, log = collected
    lock = tmp_path / "job.lock"
    run_job(
        name="daily-report",
        work=lambda: time.sleep(30),
        clock=frozen_clock(NOW),
        lock_path=lock,
        log=log,
        timeout_seconds=0.2,
    )
    with job_lock(lock):  # must not raise: a hang must not block every later run
        pass


def test_a_timeout_of_none_disables_the_alarm(tmp_path, collected):
    _, log = collected
    run = run_job(
        name="daily-report",
        work=lambda: {},
        clock=frozen_clock(NOW),
        lock_path=tmp_path / "job.lock",
        log=log,
        timeout_seconds=None,
    )
    assert run.exit_code == EXIT_OK


def test_jobtimeout_is_a_timeouterror():
    assert issubclass(JobTimeout, TimeoutError)


def test_the_log_is_one_json_object_per_line(tmp_path):
    log_path = tmp_path / "job.log"
    log = jsonl_logger(log_path)
    for index in range(3):
        run_job(
            name="daily-report",
            work=lambda i=index: {"index": i},
            clock=frozen_clock(NOW + dt.timedelta(minutes=index)),
            lock_path=tmp_path / "job.lock",
            log=log,
        )
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 3
    events = [json.loads(line) for line in lines]
    assert [e["index"] for e in events] == [0, 1, 2]
    assert {e["run_id"] for e in events} == {
        "daily-report-20260720T023000+0000",
        "daily-report-20260720T023100+0000",
        "daily-report-20260720T023200+0000",
    }


def test_only_a_success_writes_a_heartbeat(tmp_path, collected):
    _, log = collected
    heartbeat = tmp_path / "heartbeat.json"

    def failing():
        raise RuntimeError("no")

    run_job(
        name="daily-report",
        work=failing,
        clock=frozen_clock(NOW),
        lock_path=tmp_path / "job.lock",
        log=log,
        heartbeat_path=heartbeat,
    )
    assert not heartbeat.exists()

    run_job(
        name="daily-report",
        work=lambda: {},
        clock=frozen_clock(NOW),
        lock_path=tmp_path / "job.lock",
        log=log,
        heartbeat_path=heartbeat,
    )
    assert json.loads(heartbeat.read_text())["last_success"] == NOW.isoformat()


def test_a_skipped_run_still_counts_as_success(tmp_path, collected):
    """An idempotent no-op must exit 0. Alerting on it would train people to ignore alerts."""
    events, log = collected
    run = run_job(
        name="daily-report",
        work=lambda: {"status": "skipped", "action": "skipped"},
        clock=frozen_clock(NOW),
        lock_path=tmp_path / "job.lock",
        log=log,
    )
    assert run.exit_code == EXIT_OK
    assert run.status == "skipped"
    assert events[0]["status"] == "skipped"
