"""The tests for your exercises. Delete a `skip` line, then make it pass.

The first test needs no work from you — it runs green immediately, so you can
confirm your setup before you change anything. Everything after it is skipped
until you remove the decorator.

    .venv/bin/pytest starter -q          # 1 passed, 7 skipped, to begin with
    .venv/bin/pytest starter -q -k lock  # just exercise 2
"""

from __future__ import annotations

import datetime as dt
import json
import time

import pytest
from myjob import (
    AlreadyRunning,
    JobTimeout,
    append_jsonl,
    frozen_clock,
    make_event,
    my_job_lock,
    output_path,
    output_written,
    sample_payload,
    time_budget,
    write_atomically,
)

UTC = dt.timezone.utc
NOW = dt.datetime(2026, 7, 20, 2, 30, tzinfo=UTC)
DAY = dt.date(2026, 7, 19)


def test_the_setup_works():
    """No exercise here. If this passes, pytest can import your module."""
    assert output_path("/tmp/x", DAY).name == "report-2026-07-19.json"
    assert frozen_clock(NOW)() == NOW


# --- Exercise 1: idempotence ------------------------------------------------


@pytest.mark.skip(reason="Exercise 1 — delete this line when you attempt it")
def test_running_twice_leaves_exactly_one_output(tmp_path):
    assert output_written(tmp_path, DAY) is False
    first = write_atomically(sample_payload(DAY, NOW), tmp_path, DAY)
    assert output_written(tmp_path, DAY) is True
    # A second run must see the first one's work and do nothing.
    if not output_written(tmp_path, DAY):
        write_atomically(sample_payload(DAY, NOW + dt.timedelta(hours=1)), tmp_path, DAY)
    files = sorted(p.name for p in tmp_path.iterdir())
    assert files == ["report-2026-07-19.json"]
    assert json.loads(first.read_text())["generated_at"] == NOW.isoformat()


@pytest.mark.skip(reason="Exercise 1 — delete this line when you attempt it")
def test_a_partial_file_is_retried_not_skipped(tmp_path):
    """A crash mid-write must not look like a finished run for ever."""
    output_path(tmp_path, DAY).write_text('{"report_date": "2026-07-19", "read')
    assert output_written(tmp_path, DAY) is False
    write_atomically(sample_payload(DAY, NOW), tmp_path, DAY)
    assert output_written(tmp_path, DAY) is True
    assert [p.name for p in tmp_path.iterdir() if p.name.endswith(".partial")] == []


# --- Exercise 2: the lock ---------------------------------------------------


@pytest.mark.skip(reason="Exercise 2 — delete this line when you attempt it")
def test_a_second_lock_is_refused_immediately(tmp_path):
    path = tmp_path / "job.lock"
    started = time.monotonic()
    with my_job_lock(path):
        with pytest.raises(AlreadyRunning):
            with my_job_lock(path):
                pytest.fail("the second acquisition should have been refused")
    # "Refused", not "queued": a scheduled job must never wait for the lock.
    assert time.monotonic() - started < 1.0


@pytest.mark.skip(reason="Exercise 2 — delete this line when you attempt it")
def test_the_lock_is_released_even_when_the_work_raises(tmp_path):
    path = tmp_path / "job.lock"
    with pytest.raises(ValueError):
        with my_job_lock(path):
            raise ValueError("boom")
    with my_job_lock(path):
        pass  # must not raise


# --- Exercise 3: the timeout ------------------------------------------------


@pytest.mark.skip(reason="Exercise 3 — delete this line when you attempt it")
def test_a_hung_block_raises_jobtimeout_quickly():
    started = time.monotonic()
    with pytest.raises(JobTimeout):
        with time_budget(0.2):
            time.sleep(30)
    elapsed = time.monotonic() - started
    assert elapsed < 5, f"the alarm did not fire; the test waited {elapsed:.1f}s"


@pytest.mark.skip(reason="Exercise 3 — delete this line when you attempt it")
def test_a_budget_of_none_means_no_limit_and_leaves_no_alarm_armed():
    with time_budget(None):
        pass
    with time_budget(0.5):
        pass
    # If the timer were not cancelled, this sleep would be interrupted.
    time.sleep(0.7)


# --- Exercise 4: structured logging -----------------------------------------


@pytest.mark.skip(reason="Exercise 4 — delete this line when you attempt it")
def test_the_event_carries_enough_to_debug_a_run_you_did_not_watch():
    event = make_event(
        job="daily-report",
        status="ok",
        exit_code=0,
        started_at=NOW,
        finished_at=NOW + dt.timedelta(seconds=41),
        report_date=DAY.isoformat(),
    )
    for key in (
        "job",
        "run_id",
        "status",
        "exit_code",
        "started_at",
        "finished_at",
        "duration_seconds",
    ):
        assert key in event, f"the log event has no {key}"
    assert event["duration_seconds"] == 41
    assert event["report_date"] == "2026-07-19"
    assert NOW.strftime("%Y%m%d") in event["run_id"]


@pytest.mark.skip(reason="Exercise 4 — delete this line when you attempt it")
def test_the_log_is_one_json_object_per_line(tmp_path):
    path = tmp_path / "job.log"
    for index in range(3):
        append_jsonl(
            path,
            make_event(
                job="daily-report",
                status="ok",
                exit_code=0,
                started_at=NOW + dt.timedelta(minutes=index),
                finished_at=NOW + dt.timedelta(minutes=index, seconds=5),
                index=index,
            ),
        )
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 3
    assert [json.loads(line)["index"] for line in lines] == [0, 1, 2]
