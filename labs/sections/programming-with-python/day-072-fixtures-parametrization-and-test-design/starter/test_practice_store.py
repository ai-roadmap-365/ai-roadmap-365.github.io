"""The suite you have inherited. It works. That is the problem.

Every test here passes. Nothing is broken, nothing is wrong, and no reviewer
would reject it on correctness. It is still a bad suite, and your job is to
say precisely why and then fix it without losing a single assertion.

Read it once before you touch it. Count how many times the same six lines of
setup appear. Then work through `refactoring-worksheet.md`, exercise by
exercise. The finished reference lives in `../examples/` — look at it after
you have tried, not before.
"""

from datetime import date

import pytest

from practice_store import (
    MAX_MINUTES,
    DuplicateRef,
    InvalidSession,
    PracticeStore,
    Session,
    UnknownRef,
)

# --- the store tests -------------------------------------------------------
# Exercise 2 and 3 are about everything below this line up to the next banner.


def test_a_new_store_is_empty(tmp_path):
    path = tmp_path / "practice.csv"
    store = PracticeStore(path)
    store.initialise()
    assert store.all() == []
    assert store.total_minutes() == 0


def test_add_then_find_round_trips(tmp_path):
    path = tmp_path / "practice.csv"
    store = PracticeStore(path)
    store.initialise()
    added = store.add(Session("S-100", date(2026, 6, 1), "pytest", 25))
    assert store.find("S-100") == added


def test_refuses_a_duplicate_ref(tmp_path):
    path = tmp_path / "practice.csv"
    store = PracticeStore(path)
    store.initialise()
    store.add(Session("S-001", date(2026, 5, 4), "python", 45))
    store.add(Session("S-002", date(2026, 5, 5), "linear-algebra", 30))
    store.add(Session("S-003", date(2026, 5, 6), "python", 60))
    with pytest.raises(DuplicateRef):
        store.add(Session("S-001", date(2026, 7, 1), "python", 15))


def test_refuses_an_unknown_ref(tmp_path):
    path = tmp_path / "practice.csv"
    store = PracticeStore(path)
    store.initialise()
    store.add(Session("S-001", date(2026, 5, 4), "python", 45))
    store.add(Session("S-002", date(2026, 5, 5), "linear-algebra", 30))
    store.add(Session("S-003", date(2026, 5, 6), "python", 60))
    with pytest.raises(UnknownRef):
        store.find("S-999")


def test_total_minutes_for_python(tmp_path):
    path = tmp_path / "practice.csv"
    store = PracticeStore(path)
    store.initialise()
    store.add(Session("S-001", date(2026, 5, 4), "python", 45))
    store.add(Session("S-002", date(2026, 5, 5), "linear-algebra", 30))
    store.add(Session("S-003", date(2026, 5, 6), "python", 60))
    assert store.total_minutes("python") == 105


def test_total_minutes_for_linear_algebra(tmp_path):
    path = tmp_path / "practice.csv"
    store = PracticeStore(path)
    store.initialise()
    store.add(Session("S-001", date(2026, 5, 4), "python", 45))
    store.add(Session("S-002", date(2026, 5, 5), "linear-algebra", 30))
    store.add(Session("S-003", date(2026, 5, 6), "python", 60))
    assert store.total_minutes("linear-algebra") == 30


def test_total_minutes_for_everything(tmp_path):
    path = tmp_path / "practice.csv"
    store = PracticeStore(path)
    store.initialise()
    store.add(Session("S-001", date(2026, 5, 4), "python", 45))
    store.add(Session("S-002", date(2026, 5, 5), "linear-algebra", 30))
    store.add(Session("S-003", date(2026, 5, 6), "python", 60))
    assert store.total_minutes() == 135


def test_topics_come_back_sorted(tmp_path):
    path = tmp_path / "practice.csv"
    store = PracticeStore(path)
    store.initialise()
    store.add(Session("S-001", date(2026, 5, 4), "python", 45))
    store.add(Session("S-002", date(2026, 5, 5), "linear-algebra", 30))
    store.add(Session("S-003", date(2026, 5, 6), "python", 60))
    assert store.topics() == ["linear-algebra", "python"]


# --- the five near-identical rejection tests -------------------------------
# Exercise 4 is about everything below this line. Five tests, one assertion
# body, five different inputs. There is a decorator for exactly this.


def test_refuses_a_ref_without_the_prefix():
    with pytest.raises(InvalidSession):
        Session("001", date(2026, 5, 4), "python", 45)


def test_refuses_a_ref_that_is_too_short():
    with pytest.raises(InvalidSession):
        Session("S-1", date(2026, 5, 4), "python", 45)


def test_refuses_a_topic_that_is_not_lower_case():
    with pytest.raises(InvalidSession):
        Session("S-001", date(2026, 5, 4), "Python", 45)


def test_refuses_zero_minutes():
    with pytest.raises(InvalidSession):
        Session("S-001", date(2026, 5, 4), "python", 0)


def test_refuses_more_minutes_than_the_cap():
    with pytest.raises(InvalidSession):
        Session("S-001", date(2026, 5, 4), "python", MAX_MINUTES + 1)
