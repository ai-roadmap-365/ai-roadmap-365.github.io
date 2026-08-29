"""The dead man's switch: alerting on silence rather than on failure.

Each of these tests describes a real outage shape. None of them takes longer
than a millisecond, because the only thing that had to pass was time, and time
is a parameter.
"""

from __future__ import annotations

import datetime as dt
import json

from clock import frozen_clock
from watchdog import MISSING, OK, STALE, UNREADABLE, check_heartbeat

UTC = dt.timezone.utc
NOW = dt.datetime(2026, 7, 20, 9, 0, tzinfo=UTC)
BUDGET = dt.timedelta(hours=26)  # one daily interval plus a couple of hours


def write_heartbeat(path, moment):
    path.write_text(json.dumps({"job": "daily-report", "last_success": moment.isoformat()}))


def test_a_recent_success_is_quiet(tmp_path):
    path = tmp_path / "heartbeat.json"
    write_heartbeat(path, NOW - dt.timedelta(hours=7))
    verdict = check_heartbeat(heartbeat_path=path, clock=frozen_clock(NOW), max_age=BUDGET)
    assert verdict.state == OK
    assert not verdict.alerting


def test_one_missed_run_is_tolerated(tmp_path):
    """A single late run should not page anyone. Two intervals is the usual budget."""
    path = tmp_path / "heartbeat.json"
    write_heartbeat(path, NOW - dt.timedelta(hours=25))
    assert check_heartbeat(
        heartbeat_path=path, clock=frozen_clock(NOW), max_age=BUDGET
    ).state == OK


def test_a_job_that_stopped_two_days_ago_alerts(tmp_path):
    """The outage nothing else catches: the job was removed and never ran again.

    No failure, no traceback, no non-zero exit — because there was no run.
    Only the absence of a success says anything at all.
    """
    path = tmp_path / "heartbeat.json"
    write_heartbeat(path, NOW - dt.timedelta(days=2))
    verdict = check_heartbeat(heartbeat_path=path, clock=frozen_clock(NOW), max_age=BUDGET)
    assert verdict.state == STALE
    assert verdict.alerting
    assert "stopped running" in verdict.message
    assert verdict.age_seconds == 2 * 86400


def test_a_job_that_never_ran_at_all_alerts(tmp_path):
    verdict = check_heartbeat(
        heartbeat_path=tmp_path / "nothing.json", clock=frozen_clock(NOW), max_age=BUDGET
    )
    assert verdict.state == MISSING
    assert verdict.alerting


def test_a_corrupt_heartbeat_alerts_rather_than_passing(tmp_path):
    path = tmp_path / "heartbeat.json"
    path.write_text("{ this is not json")
    assert check_heartbeat(
        heartbeat_path=path, clock=frozen_clock(NOW), max_age=BUDGET
    ).state == UNREADABLE


def test_a_naive_timestamp_is_refused_rather_than_guessed(tmp_path):
    """Comparing an aware 'now' with a naive record would raise; guessing would lie."""
    path = tmp_path / "heartbeat.json"
    path.write_text(json.dumps({"last_success": "2026-07-20T08:00:00"}))
    verdict = check_heartbeat(
        heartbeat_path=path, clock=frozen_clock(NOW), max_age=BUDGET
    )
    assert verdict.state == UNREADABLE
    assert "naive" in verdict.message


def test_the_boundary_is_exact(tmp_path):
    path = tmp_path / "heartbeat.json"
    write_heartbeat(path, NOW - BUDGET)
    assert check_heartbeat(
        heartbeat_path=path, clock=frozen_clock(NOW), max_age=BUDGET
    ).state == OK
    write_heartbeat(path, NOW - BUDGET - dt.timedelta(seconds=1))
    assert check_heartbeat(
        heartbeat_path=path, clock=frozen_clock(NOW), max_age=BUDGET
    ).state == STALE
