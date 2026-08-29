"""Reference solutions -- Day 134, "Judge the Source Before the Data".

Nine exercises. Each asserts on real behaviour: a real mock HTTP server
answering real requests, or a real checksum of real bytes -- never on
source code, and never on a value nobody computed.

Run with: pytest examples -q
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

import datasource as ds
import fixtures as fx
from mock_server import PAGE_SIZE, TOTAL_ROWS


def test_01_the_definition_trap():
    """Two columns named unemployment_rate, defined differently.

    The naive dtype-and-range check passes on both -- nothing mechanical
    would flag the join. Only the dictionary-aware check, which reads the
    prose definition rather than the numbers, refuses it.
    """
    series_a = fx.unemployment_series_a()
    series_b = fx.unemployment_series_b()

    naive = ds.naive_join_check(series_a, series_b)
    assert naive["dtype_match"] is True
    assert naive["ranges_overlap"] is True
    assert naive["would_pass_naive_check"] is True

    aware = ds.dictionary_aware_join_check(fx.DICTIONARY_A, fx.DICTIONARY_B, "unemployment_rate")
    assert aware["same_definition"] is False
    assert aware["safe_to_join"] is False
    assert "differ" in aware["reason"]
    assert "actively seeking" in aware["reason"]
    assert "regardless of whether" in aware["reason"]


def test_02_pagination_to_exhaustion(mock_api):
    """The client follows pages until the source says stop, not a fixed count."""
    rows = ds.fetch_all_pages(mock_api.base_url, "/dataset")

    assert len(rows) == TOTAL_ROWS
    assert [row["id"] for row in rows] == list(range(TOTAL_ROWS))

    expected_pages = -(-TOTAL_ROWS // PAGE_SIZE)  # ceiling division
    assert mock_api.request_log.count("/dataset") == expected_pages


def test_03_rate_limiting(mock_api, stubborn_mock_api):
    """A 429 triggers bounded backoff and eventual success; the client gives up."""
    body, attempts = ds.fetch_with_backoff(
        mock_api.base_url, "/ratelimited", max_attempts=5, base_delay=0.01
    )
    payload = json.loads(body)

    assert payload["ok"] is True
    assert attempts == 3  # 2 rejections (mock_api's trigger count) then success
    assert mock_api.rate_limit_hits == [1, 2]

    with pytest.raises(ds.RateLimitExceeded):
        ds.fetch_with_backoff(
            stubborn_mock_api.base_url, "/ratelimited", max_attempts=3, base_delay=0.01
        )
    # It tried exactly 3 times (the budget) and no more, against a source
    # that would have kept saying 429 forever.
    assert stubborn_mock_api.rate_limit_hits == [1, 2, 3]


def test_04_conditional_request(mock_api):
    """A second fetch with the stored ETag returns 304 and costs zero bytes."""
    cache: dict[str, ds.CacheEntry] = {}

    first_body, first_from_cache, first_bytes = ds.fetch_with_etag(
        mock_api.base_url, "/etag-resource", cache
    )
    assert first_from_cache is False
    assert first_bytes > 0  # the real payload went over the wire

    second_body, second_from_cache, second_bytes = ds.fetch_with_etag(
        mock_api.base_url, "/etag-resource", cache
    )
    assert second_from_cache is True
    assert second_body == first_body  # the cached copy is served, unchanged
    assert second_bytes == 0  # a 304 carries no body -- the re-run cost nothing

    assert mock_api.request_log.count("/etag-resource") == 2


def test_05_checksum_pinning(tmp_path):
    """The SHA-256 of a fixture matches a recorded value; one byte breaks it."""
    original = tmp_path / "dataset.csv"
    original.write_text("id,value\n1,10\n2,20\n3,30\n")

    digest = ds.sha256_of(original)
    assert digest == "4c0610aa92b75ca794ceec30068934fc6bc3d2fbff87969a15977f8fcf96f13f"

    altered = tmp_path / "altered.csv"
    altered.write_text("id,value\n1,10\n2,20\n3,31\n")  # one digit changed
    altered_digest = ds.sha256_of(altered)

    assert altered_digest == "9352ed755477b7af1eefd6e473c3880dd49e0a5d368846f51f8d96519d2bcf50"
    assert altered_digest != digest


def test_06_five_minute_source_assessment():
    """The structured verdict distinguishes a documented source from an undocumented one."""
    good_verdict = ds.assess_source(fx.GOOD_SOURCE_METADATA)
    assert good_verdict.ready is True
    assert good_verdict.problems == []
    assert good_verdict.granularity == "monthly, per region"
    assert good_verdict.dictionary_present is True

    deficient_verdict = ds.assess_source(fx.DEFICIENT_SOURCE_METADATA)
    assert deficient_verdict.ready is False
    assert "no stated coverage" in deficient_verdict.problems
    assert "no stated licence" in deficient_verdict.problems
    assert "no data dictionary" in deficient_verdict.problems
    assert "no update cadence" in deficient_verdict.problems
    assert "known issues undocumented" in deficient_verdict.problems


def test_07_licence_gate():
    """Redistribution passes for CC0, fails for 'all rights reserved' -- with a reason."""
    cc0 = ds.check_licence("CC0", purpose="redistribution")
    assert cc0["allowed"] is True
    assert "CC0" in cc0["reason"]

    ccby = ds.check_licence("CC-BY-4.0", purpose="redistribution")
    assert ccby["allowed"] is True
    assert "attribution" in ccby["reason"]

    odbl = ds.check_licence("ODbL", purpose="redistribution")
    assert odbl["allowed"] is True
    assert "share-alike" in odbl["reason"]

    all_rights = ds.check_licence("All rights reserved", purpose="redistribution")
    assert all_rights["allowed"] is False
    assert "forbids" in all_rights["reason"]
    assert all_rights["reason"] != ""  # a reason, never a bare boolean


def test_08_coverage_check():
    """A dataset claiming national coverage is missing a region -- caught by key comparison."""
    result = ds.check_coverage(fx.DICTIONARY_A, fx.NATIONAL_DATASET_KEYS)

    assert result["complete"] is False
    assert result["missing"] == ["west"]
    assert result["expected"] == ["east", "north", "south", "west"]

    complete_result = ds.check_coverage(fx.DICTIONARY_A, {"north", "south", "east", "west"})
    assert complete_result["complete"] is True
    assert complete_result["missing"] == []


def test_09_provenance_record(tmp_path):
    """The record carries url, retrieval timestamp and checksum, and is stable
    once the timestamp is held fixed rather than left to the clock."""
    payload = tmp_path / "dataset.csv"
    payload.write_text("id,value\n1,10\n2,20\n3,30\n")
    checksum = ds.sha256_of(payload)
    fixed_moment = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    record_one = ds.record_provenance(
        "http://example.test/dataset.csv", checksum, retrieved_at=fixed_moment
    )
    record_two = ds.record_provenance(
        "http://example.test/dataset.csv", checksum, retrieved_at=fixed_moment
    )

    assert set(record_one) == {"url", "retrieved_at", "sha256"}
    assert record_one["url"] == "http://example.test/dataset.csv"
    assert record_one["sha256"] == checksum
    # Regenerating from the same fixture with the same injected timestamp
    # is byte-identical -- the flaky part (the real clock) is handled by
    # letting the caller pin it explicitly rather than asserting on `now()`.
    assert record_one == record_two

    # Without a pinned timestamp the function still returns a well-formed
    # ISO-8601 string -- it does not crash, it just won't compare equal
    # to a call made a second later, which is expected and not tested here.
    natural_record = ds.record_provenance("http://example.test/dataset.csv", checksum)
    assert natural_record["url"] == record_one["url"]
    assert natural_record["sha256"] == record_one["sha256"]
    datetime.fromisoformat(natural_record["retrieved_at"])  # parses without error
