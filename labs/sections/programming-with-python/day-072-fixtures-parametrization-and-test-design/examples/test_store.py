"""The behaviour of the store, driven entirely through fixtures.

Compare this file with `starter/test_practice_store.py`. They test the same
things. This one has no copy-pasted setup, because every arrangement it needs
has a name and lives in `conftest.py`.
"""

from datetime import date

import pytest

from practice_store import DuplicateRef, Session, UnknownRef


def test_a_new_store_is_empty(empty_store):
    assert empty_store.all() == []
    assert empty_store.total_minutes() == 0


def test_add_then_find_round_trips(empty_store):
    added = empty_store.add(Session("S-100", date(2026, 6, 1), "pytest", 25))
    assert empty_store.find("S-100") == added


def test_refuses_a_duplicate_ref(loaded_store):
    with pytest.raises(DuplicateRef):
        loaded_store.add(Session("S-001", date(2026, 7, 1), "python", 15))


def test_refuses_an_unknown_ref(loaded_store):
    with pytest.raises(UnknownRef):
        loaded_store.find("S-999")


@pytest.mark.parametrize(
    ("topic", "expected"),
    [("python", 105), ("linear-algebra", 30), (None, 135)],
    ids=["python-only", "linear-algebra-only", "every-topic"],
)
def test_total_minutes_adds_the_right_sessions(loaded_store, topic, expected):
    assert loaded_store.total_minutes(topic) == expected


def test_topics_come_back_sorted(loaded_store):
    assert loaded_store.topics() == ["linear-algebra", "python"]


def test_teardown_reports_the_final_size(audited_store):
    audited_store.add(Session("S-004", date(2026, 5, 7), "pytest", 20))
    assert len(audited_store.all()) == 4


@pytest.mark.slow
def test_the_file_on_disk_is_plain_readable_csv(loaded_store):
    text = loaded_store.path.read_text(encoding="utf-8")
    header, first, *_ = text.splitlines()
    assert header == "ref,logged_on,topic,minutes"
    assert first == "S-001,2026-05-04,python,45"
