"""The rules of one Session, expressed as parametrized tests.

Every test in this module is about a value, not about a file, so not one of
them asks for a store or a path. That is the first sign of a suite that has
been designed rather than accumulated: the cheap tests stay cheap.
"""

from datetime import date, timedelta

import pytest

from practice_store import MAX_MINUTES, InvalidSession, Session

# Applies the `validation` marker to every test in this module at once, so
# `pytest -m validation` selects the whole file without repeating a decorator.
pytestmark = pytest.mark.validation


@pytest.mark.parametrize(
    "minutes",
    [1, 45, MAX_MINUTES],
    ids=["shortest-allowed", "typical", "longest-allowed"],
)
def test_accepts_a_valid_session(minutes):
    session = Session("S-001", date(2026, 5, 4), "python", minutes)
    assert session.minutes == minutes


@pytest.mark.parametrize(
    ("ref", "topic", "minutes"),
    [
        ("001", "python", 45),
        ("S-1", "python", 45),
        ("S-001", "Python", 45),
        ("S-001", " python ", 45),
        ("S-001", "python", 0),
        ("S-001", "python", MAX_MINUTES + 1),
    ],
    ids=[
        "ref-without-prefix",
        "ref-too-short",
        "topic-not-lower-case",
        "topic-padded-with-spaces",
        "minutes-zero",
        "minutes-over-the-cap",
    ],
)
def test_refuses_a_bad_value(ref, topic, minutes):
    with pytest.raises(InvalidSession):
        Session(ref, date(2026, 5, 4), topic, minutes)


# Two stacked decorators produce the cross product: every topic is combined
# with every duration, so three and three become nine independent test items.
@pytest.mark.parametrize("topic", ["python", "linear-algebra", "statistics"])
@pytest.mark.parametrize("minutes", [1, 45, MAX_MINUTES])
def test_every_topic_accepts_every_legal_duration(topic, minutes):
    session = Session("S-001", date(2026, 5, 4), topic, minutes)
    assert session.topic == topic
    assert 0 < session.minutes <= MAX_MINUTES


@pytest.mark.parametrize(
    "logged_on",
    [
        date(2026, 5, 4),
        date(1999, 1, 1),
        pytest.param(
            date(2026, 5, 4) + timedelta(days=3650),
            marks=pytest.mark.xfail(
                strict=True,
                reason="the stated rules never forbade a session dated in the future",
            ),
        ),
    ],
    ids=["today-ish", "long-ago", "far-future"],
)
def test_refuses_a_date_outside_the_practice_log(logged_on):
    """The third case is a known gap, recorded rather than quietly ignored.

    `strict=True` means the suite fails if this case ever starts passing —
    which is what you want, because that is the day somebody implemented the
    rule and forgot to delete the marker.
    """
    session = Session("S-001", logged_on, "python", 45)
    assert session.logged_on <= date(2026, 5, 4)
