"""Your exercises for Day 134 -- "Judge the Source Before the Data".

Nine exercises. Every test below currently calls `pytest.skip(...)` --
replace the skip with real assertions and delete the skip line. Read
`00_brief.md` for the exercise-by-exercise explanation, `datasource.py`
for the client and judgement functions you are testing, `mock_server.py`
for the mock API they talk to, and `fixtures.py` for the fixture data.

Check yourself at any point:

    pytest starter -v

The reference answer key lives in `examples/test_datasource.py` -- read it
AFTER you have tried, never before.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

import datasource as ds
import fixtures as fx
from mock_server import PAGE_SIZE, TOTAL_ROWS


def test_01_the_definition_trap():
    pytest.skip(
        "Take fx.unemployment_series_a() and fx.unemployment_series_b(). Run "
        "ds.naive_join_check(series_a, series_b) and assert dtype_match, "
        "ranges_overlap and would_pass_naive_check are all True -- nothing "
        "mechanical flags the join. Then run "
        "ds.dictionary_aware_join_check(fx.DICTIONARY_A, fx.DICTIONARY_B, "
        "'unemployment_rate') and assert same_definition and safe_to_join are "
        "both False, and that the reason string contains 'differ'"
    )


def test_02_pagination_to_exhaustion(mock_api):
    pytest.skip(
        "Call ds.fetch_all_pages(mock_api.base_url, '/dataset') and assert the "
        "number of rows returned equals TOTAL_ROWS, and that the ids form "
        "range(TOTAL_ROWS) in order. Then assert "
        "mock_api.request_log.count('/dataset') equals the number of pages "
        "needed to cover TOTAL_ROWS at PAGE_SIZE per page (ceiling division)"
    )


def test_03_rate_limiting(mock_api, stubborn_mock_api):
    pytest.skip(
        "Call ds.fetch_with_backoff(mock_api.base_url, '/ratelimited', "
        "max_attempts=5, base_delay=0.01) and assert the decoded JSON body has "
        "ok=True and that attempts equals 3 (2 rejections then success). Assert "
        "mock_api.rate_limit_hits == [1, 2]. Then assert that calling "
        "ds.fetch_with_backoff(stubborn_mock_api.base_url, '/ratelimited', "
        "max_attempts=3, base_delay=0.01) raises ds.RateLimitExceeded, and that "
        "stubborn_mock_api.rate_limit_hits == [1, 2, 3] -- it tried exactly the "
        "budget and no more"
    )


def test_04_conditional_request(mock_api):
    pytest.skip(
        "Create an empty cache dict. Call ds.fetch_with_etag(mock_api.base_url, "
        "'/etag-resource', cache) once and assert served_from_cache is False and "
        "bytes_over_wire is greater than 0. Call it again with the same cache "
        "and assert served_from_cache is True, the returned body is unchanged, "
        "and bytes_over_wire equals 0 -- a 304 carries no body, so the re-run "
        "cost nothing"
    )


def test_05_checksum_pinning(tmp_path):
    pytest.skip(
        "Write 'id,value\\n1,10\\n2,20\\n3,30\\n' to a file in tmp_path, compute "
        "ds.sha256_of(that_file), and assert it equals the recorded 64-character "
        "hex digest (compute it once with hashlib.sha256(...).hexdigest() and "
        "pin the value here -- do not guess it). Then write the same content "
        "with one digit changed to a second file, compute its digest, and "
        "assert it differs from the first"
    )


def test_06_five_minute_source_assessment():
    pytest.skip(
        "Call ds.assess_source(fx.GOOD_SOURCE_METADATA) and assert .ready is "
        "True and .problems is empty. Call ds.assess_source("
        "fx.DEFICIENT_SOURCE_METADATA) and assert .ready is False and that "
        "'no stated coverage', 'no stated licence', 'no data dictionary' and "
        "'no update cadence' are all in .problems"
    )


def test_07_licence_gate():
    pytest.skip(
        "Call ds.check_licence('CC0', purpose='redistribution') and assert "
        "allowed is True. Call ds.check_licence('All rights reserved', "
        "purpose='redistribution') and assert allowed is False and that the "
        "reason string is non-empty and contains 'forbids' -- the function "
        "must return a reason, never a bare boolean"
    )


def test_08_coverage_check():
    pytest.skip(
        "Call ds.check_coverage(fx.DICTIONARY_A, fx.NATIONAL_DATASET_KEYS) and "
        "assert complete is False and missing equals ['west'] -- detected by "
        "comparing the dictionary's expected_regions against the actual keys, "
        "not by looking at a chart. Then call it again with all four regions "
        "present and assert complete is True"
    )


def test_09_provenance_record(tmp_path):
    pytest.skip(
        "Write a small CSV to tmp_path and compute its checksum. Call "
        "ds.record_provenance(url, checksum, retrieved_at=some_fixed_datetime) "
        "twice with the SAME fixed timestamp and assert the two records are "
        "equal -- regenerating from the same fixture is stable once the clock "
        "is pinned. Assert the record has exactly the keys url, retrieved_at "
        "and sha256"
    )
