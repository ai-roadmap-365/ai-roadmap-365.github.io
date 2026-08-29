"""Daylight saving, tested in milliseconds because the clock is a parameter.

Waiting for 2 November to find out what a job does on 1 November is not a
plan. These tests ask the operating system's own time zone database what the
transitions are, and assert on the answer.
"""

from __future__ import annotations

import datetime as dt

from timezones import classify_wall_time, daily_instants_local, gaps_between

UTC = dt.timezone.utc
ZONE = "America/New_York"


def test_an_ordinary_wall_time_happens_exactly_once():
    verdict = classify_wall_time(dt.datetime(2026, 7, 19, 2, 30), ZONE)
    assert verdict.kind == "normal"
    assert len(verdict.instants) == 1


def test_0230_does_not_exist_on_the_spring_forward_morning():
    """2026-03-08: US clocks jump 02:00 to 03:00, so 02:30 never happens.

    A daily job at 02:30 local time therefore has no instant to run at, and
    Python resolves the impossible wall time to 03:30 local — an hour later
    than anyone intended.
    """
    verdict = classify_wall_time(dt.datetime(2026, 3, 8, 2, 30), ZONE)
    assert verdict.kind == "skipped"
    assert not verdict.exists
    assert verdict.instants[0] == dt.datetime(2026, 3, 8, 7, 30, tzinfo=UTC)


def test_0130_happens_twice_on_the_fall_back_morning():
    """2026-11-01: 01:30 occurs once as EDT and again an hour later as EST."""
    verdict = classify_wall_time(dt.datetime(2026, 11, 1, 1, 30), ZONE)
    assert verdict.kind == "repeated"
    assert verdict.instants == (
        dt.datetime(2026, 11, 1, 5, 30, tzinfo=UTC),
        dt.datetime(2026, 11, 1, 6, 30, tzinfo=UTC),
    )
    assert (verdict.instants[1] - verdict.instants[0]) == dt.timedelta(hours=1)


def test_a_local_daily_schedule_has_a_23_hour_and_a_25_hour_day():
    spring = gaps_between(
        daily_instants_local(
            start_date=dt.date(2026, 3, 6), days=5, hour=12, minute=0, zone_name=ZONE
        )
    )
    autumn = gaps_between(
        daily_instants_local(
            start_date=dt.date(2026, 10, 30), days=5, hour=12, minute=0, zone_name=ZONE
        )
    )
    assert 23.0 in spring, spring
    assert 25.0 in autumn, autumn


def test_a_utc_schedule_is_always_exactly_24_hours():
    """The whole argument for UTC, in one assertion."""
    for start in (dt.date(2026, 3, 6), dt.date(2026, 10, 30)):
        gaps = gaps_between(
            daily_instants_local(
                start_date=start, days=5, hour=12, minute=0, zone_name="UTC"
            )
        )
        assert set(gaps) == {24.0}
