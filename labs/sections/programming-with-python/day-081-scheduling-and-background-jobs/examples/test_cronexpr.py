"""The cron expression tests, including the field everybody gets wrong."""

from __future__ import annotations

import datetime as dt

import pytest
from cronexpr import CronError, parse

UTC = dt.timezone.utc


def at(year, month, day, hour=0, minute=0):
    return dt.datetime(year, month, day, hour, minute, tzinfo=UTC)


def test_five_fields_are_required():
    with pytest.raises(CronError, match="expected 5 fields"):
        parse("30 2 * *")


def test_a_field_outside_its_range_is_rejected_not_ignored():
    with pytest.raises(CronError, match="outside 0-23"):
        parse("0 24 * * *")


def test_a_typo_raises_rather_than_silently_meaning_every_minute():
    with pytest.raises(CronError):
        parse("*/ 2 * * *")


@pytest.mark.parametrize(
    ("expression", "moment", "expected"),
    [
        ("30 2 * * *", at(2026, 7, 19, 2, 30), True),
        ("30 2 * * *", at(2026, 7, 19, 2, 31), False),
        ("*/15 * * * *", at(2026, 7, 19, 9, 45), True),
        ("*/15 * * * *", at(2026, 7, 19, 9, 46), False),
        ("0 9-17 * * 1-5", at(2026, 7, 20, 9, 0), True),  # a Monday
        ("0 9-17 * * 1-5", at(2026, 7, 19, 9, 0), False),  # a Sunday: only one day field is set, so AND
        ("0 0 1 1 *", at(2027, 1, 1, 0, 0), True),
    ],
)
def test_matching(expression, moment, expected):
    assert parse(expression).matches(moment) is expected


def test_sunday_is_both_zero_and_seven():
    assert parse("0 3 * * 0").days_of_week == parse("0 3 * * 7").days_of_week


def test_day_of_month_and_day_of_week_are_ORed_not_ANDed():
    """The famous gotcha: `0 0 13 * 5` is the 13th OR any Friday, not Friday the 13th.

    2026-11-13 is a Friday, so it matches on both counts. 2026-07-13 is a
    Monday and matches only the day-of-month. 2026-07-17 is a Friday and
    matches only the day-of-week. Under an AND reading the last two would not
    fire at all — and a job written that way runs about eight times more often
    than its author expected.
    """
    schedule = parse("0 0 13 * 5")
    assert schedule.dom_restricted and schedule.dow_restricted
    assert schedule.matches(at(2026, 11, 13))  # Friday the 13th: both
    assert schedule.matches(at(2026, 7, 13))  # a Monday: day-of-month only
    assert schedule.matches(at(2026, 7, 17))  # a Friday: day-of-week only
    assert not schedule.matches(at(2026, 7, 14))  # neither


def test_only_one_of_the_two_day_fields_restricted_means_AND():
    schedule = parse("0 0 * * 5")  # every Friday
    assert schedule.matches(at(2026, 7, 17))
    assert not schedule.matches(at(2026, 7, 13))


def test_next_run_after_a_daily_schedule():
    schedule = parse("30 2 * * *")
    assert schedule.next_run_after(at(2026, 7, 19, 1, 0)) == at(2026, 7, 19, 2, 30)
    assert schedule.next_run_after(at(2026, 7, 19, 2, 30)) == at(2026, 7, 20, 2, 30)


def test_next_run_skips_to_the_right_weekday():
    schedule = parse("0 6 * * 1")  # Mondays at 06:00
    # 2026-07-19 is a Sunday; the next Monday is the 20th.
    assert schedule.next_run_after(at(2026, 7, 19, 12, 0)) == at(2026, 7, 20, 6, 0)


def test_describe_names_the_or_rule():
    assert "OR" in parse("0 0 13 * 5").describe()
    assert "OR" not in parse("30 2 * * *").describe()
