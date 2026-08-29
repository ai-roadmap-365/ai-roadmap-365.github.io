"""Drift, measured — and a `sched` schedule run through six hours in no time."""

from __future__ import annotations

from clock import FakeTime
from inprocess import (
    deadline_corrected_loop,
    naive_sleep_loop,
    periodic_with_sched,
    run_sched_schedule,
)


def test_the_naive_sleep_loop_drifts_by_the_work_duration_every_run():
    """`work(); sleep(60)` with 5 seconds of work is a 65-second schedule.

    Nobody wrote 65 anywhere. After 100 runs the job is 495 seconds — more
    than eight minutes — behind where its author believes it is, and the
    error grows without limit.
    """
    trace = naive_sleep_loop(runs=100, interval=60, work_seconds=5)
    assert trace.lateness[0] == 0
    assert trace.lateness[1] == 5
    assert trace.final_drift == 495
    assert trace.starts[1] - trace.starts[0] == 65


def test_the_deadline_corrected_loop_does_not_drift():
    trace = deadline_corrected_loop(runs=100, interval=60, work_seconds=5)
    assert set(trace.lateness) == {0}
    assert trace.starts[1] - trace.starts[0] == 60


def test_a_run_longer_than_the_interval_makes_the_next_one_immediate():
    """Correction cannot invent time: overrun means the next run starts at once."""
    trace = deadline_corrected_loop(runs=5, interval=10, work_seconds=25)
    assert trace.starts[1] - trace.starts[0] == 25
    assert trace.final_drift > 0  # honest: this schedule cannot be met


def test_sched_runs_a_six_hour_schedule_instantly():
    fired, fake = run_sched_schedule(delays=[3600, 7200, 21600])
    assert [index for _, index in fired] == [0, 1, 2]
    assert [when for when, _ in fired] == [3600, 7200, 21600]
    assert fake.total_slept == 21600  # six hours "waited", zero seconds spent


def test_sched_runs_events_in_time_order_not_insertion_order():
    fired, _ = run_sched_schedule(delays=[300, 60, 120])
    assert [index for _, index in fired] == [1, 2, 0]


def test_a_recurring_sched_job_re_enters_itself_without_drifting():
    fake = FakeTime()
    starts = periodic_with_sched(
        interval=900, runs=8, work=lambda: fake.sleep(11), fake=fake
    )
    assert starts == [0, 900, 1800, 2700, 3600, 4500, 5400, 6300]
