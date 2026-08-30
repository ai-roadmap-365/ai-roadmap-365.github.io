"""Grouped by control, so a failure names which one broke.

Every identifier here is synthetic and invalid by construction: example.com is
a reserved domain, 192.0.2.0/24 is the reserved TEST-NET-1 range, and the card
number fails the Luhn check.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from privacy import (  # noqa: E402
    Category,
    DataFlow,
    erase,
    minimise,
    pseudonym,
    redact,
)


# ----------------------------------------------------------------- detection


def test_each_category_is_detected():
    text = (
        "mail ada@example.com call +44 7700 900123 card 4111 1111 1111 1111 "
        "ssn 123-45-6789 host 192.0.2.44"
    )
    result = redact(text)
    for category in Category:
        assert result.count(category) == 1, f"{category.value} not detected exactly once"


def test_nothing_of_the_original_identifier_survives():
    # The real test of a redactor: not "did it find something" but "is any of
    # it left". A partial redaction reads as a success and leaks anyway.
    #
    # Fragments must be chosen so they CANNOT appear in a hex digest by
    # coincidence -- "ada" is valid hex and shows up in tokens by chance, which
    # would make this test fail on a correct redactor.
    text = "ada@example.com / +44 7700 900123 / 123-45-6789 / 192.0.2.44"
    out = redact(text).text
    for fragment in ("ada@", "example.com", "900123", "123-45-6789", "192.0.2"):
        assert fragment not in out, f"{fragment!r} survived redaction"


def test_leading_plus_on_a_phone_number_is_consumed():
    # A word boundary cannot match before "+", so a naive \b pattern leaves a
    # bare "+" behind. Cosmetic on its own, and a signal the match was partial.
    out = redact("Phone: +44 7700 900123").text
    assert "+" not in out


def test_clean_text_is_left_alone():
    text = "The refund window is thirty days from purchase."
    result = redact(text)
    assert result.text == text
    assert result.summary() == "clean"


def test_card_is_not_partly_consumed_by_the_phone_detector():
    # Ordering matters: the longer, more specific pattern must run first.
    result = redact("card 4111 1111 1111 1111 only")
    assert result.count(Category.CARD) == 1
    assert result.count(Category.PHONE) == 0


# --------------------------------------------------------------- pseudonyms


def test_pseudonym_is_stable_for_the_same_value():
    a = redact("write to ada@example.com").findings[0].token
    b = redact("ada@example.com replied").findings[0].token
    assert a == b, "the same person must be recognisable across records"


def test_pseudonym_differs_for_different_values():
    a = pseudonym("ada@example.com", Category.EMAIL)
    b = pseudonym("grace@example.com", Category.EMAIL)
    assert a != b


def test_pseudonym_is_salted():
    # Without a salt, a hash of a short value is reversed by enumerating the
    # space -- there are only so many phone numbers.
    assert pseudonym("x", Category.EMAIL, salt="a") != pseudonym("x", Category.EMAIL, salt="b")


def test_pseudonym_does_not_contain_the_original():
    # Assert on the whole value and on fragments containing non-hex characters.
    # A short all-hex fragment such as "ada" appears in digests by coincidence,
    # so testing for it would fail against a perfectly good redactor.
    token = pseudonym("ada@example.com", Category.EMAIL)
    assert "ada@example.com" not in token
    assert "example" not in token
    assert "@" not in token


# --------------------------------------------------------------- data flow


def test_flow_records_every_store_a_subject_reached():
    flow = DataFlow()
    for store in ("database", "vector_index", "response_cache", "audit_log"):
        flow.record(store, "s1")
    assert flow.where("s1") == {"database", "vector_index", "response_cache", "audit_log"}


def test_flow_is_per_subject():
    flow = DataFlow()
    flow.record("database", "s1")
    flow.record("audit_log", "s2")
    assert flow.where("s1") == {"database"}
    assert flow.where("s2") == {"audit_log"}


def test_recording_twice_does_not_duplicate():
    flow = DataFlow()
    flow.record("database", "s1")
    flow.record("database", "s1")
    assert flow.stores["database"] == {"s1"}


# ----------------------------------------------------------------- erasure


def test_partial_erasure_is_reported_as_incomplete():
    # The failure this whole lab exists for: deleting from the stores someone
    # remembered, and reporting success.
    flow = DataFlow()
    for store in ("database", "vector_index", "response_cache", "audit_log"):
        flow.record(store, "s1")

    report = erase(flow, "s1", stores=["database", "vector_index"])
    assert report.complete is False
    assert report.still_present == ["audit_log", "response_cache"]


def test_full_erasure_is_verified_not_assumed():
    flow = DataFlow()
    for store in ("database", "vector_index", "response_cache", "audit_log"):
        flow.record(store, "s1")

    erase(flow, "s1", stores=["database", "vector_index"])
    report = erase(flow, "s1")
    assert report.complete is True
    assert flow.where("s1") == set()


def test_erasure_reports_only_stores_it_actually_removed_from():
    flow = DataFlow()
    flow.record("database", "s1")
    report = erase(flow, "s1", stores=["database", "vector_index"])
    assert report.deleted_from == ["database"]


def test_erasing_an_unknown_subject_is_complete_and_harmless():
    flow = DataFlow()
    flow.record("database", "s1")
    report = erase(flow, "nobody")
    assert report.complete is True
    assert flow.where("s1") == {"database"}


# ------------------------------------------------------------ minimisation


def test_minimise_keeps_only_the_named_fields():
    record = {"name": "Ada", "email": "ada@example.com", "tier": "pro"}
    assert minimise(record, {"tier"}) == {"tier": "pro"}


def test_minimise_ignores_fields_that_are_absent():
    assert minimise({"tier": "pro"}, {"tier", "missing"}) == {"tier": "pro"}


def test_minimise_can_keep_nothing():
    assert minimise({"name": "Ada"}, set()) == {}
