"""The reference suite, run against the local test server on 127.0.0.1.

Every test here opens a real socket — to a server this process started, on
a port the operating system chose, serving fixture data. None of them
touches the internet, and none of them is slow: the whole file finishes in
well under a second because the only "slow" endpoint is used precisely to
prove that a timeout fires.
"""

from __future__ import annotations

import time

import pytest
import requests

from client import (
    DEFAULT_TIMEOUT,
    RETRY_STATUSES,
    Reading,
    ReadingsUnavailable,
    StationNotFound,
    backoff_delays,
    describe_failure,
    fetch_readings,
    get_with_retry,
    make_session,
    stream_to_file,
    summarise,
)


class RecordingSleep:
    def __init__(self) -> None:
        self.waits: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.waits.append(round(seconds, 4))


@pytest.fixture
def session():
    s = make_session()
    yield s
    s.close()


# --- 1. fetch and parse JSON ------------------------------------------------


def test_fetch_readings_returns_parsed_objects(base, session):
    readings = fetch_readings(base, "ALPHA", session=session)
    assert len(readings) == 4
    assert all(isinstance(r, Reading) for r in readings)
    assert readings[0] == Reading(station="ALPHA", hour=0, celsius=12.0)


def test_summary_of_the_fetched_readings(base, session):
    assert summarise(fetch_readings(base, "ALPHA", session=session)) == {
        "count": 4.0,
        "min": 12.0,
        "max": 22.0,
        "mean": 17.0,
    }


def test_params_are_encoded_not_concatenated(base, session):
    awkward = "ALPHA ONE&station=BRAVO"
    good = session.get(f"{base}/api/search", params={"station": awkward}, timeout=DEFAULT_TIMEOUT)
    assert good.json()["parsed"]["station"] == [awkward]
    assert good.json()["raw_query"] == "station=ALPHA+ONE%26station%3DBRAVO"
    bad = session.get(f"{base}/api/search?station={awkward}", timeout=DEFAULT_TIMEOUT)
    # The unencoded ampersand became a second parameter the caller never meant.
    assert bad.json()["parsed"]["station"] == ["ALPHA ONE", "BRAVO"]


def test_text_content_and_json_are_three_different_things(base, session):
    response = session.get(f"{base}/api/readings", timeout=DEFAULT_TIMEOUT)
    assert isinstance(response.content, bytes)
    assert isinstance(response.text, str)
    assert isinstance(response.json(), dict)
    assert response.content.decode("utf-8") == response.text


# --- 2. a 404 handled without a traceback -----------------------------------


def test_a_404_is_a_successful_response_not_an_exception(base, session):
    response = session.get(f"{base}/api/missing", timeout=DEFAULT_TIMEOUT)
    assert response.status_code == 404
    assert bool(response) is False


def test_a_missing_station_raises_a_domain_error_with_a_clean_message(base, session):
    with pytest.raises(StationNotFound) as caught:
        fetch_readings(base, "NOWHERE", session=session)
    assert "NOWHERE" in str(caught.value)
    assert "Traceback" not in str(caught.value)


def test_describe_failure_says_something_a_human_can_act_on(base, session):
    missing = session.get(f"{base}/api/missing", timeout=DEFAULT_TIMEOUT)
    assert describe_failure(missing) == "HTTP 404 (your request was rejected) — no such station"
    broken = session.get(f"{base}/api/broken", timeout=DEFAULT_TIMEOUT)
    assert describe_failure(broken) == "HTTP 500 (the server failed) — the server fell over"


def test_raise_for_status_raises_on_500_and_is_silent_on_200(base, session):
    with pytest.raises(requests.exceptions.HTTPError):
        session.get(f"{base}/api/broken", timeout=DEFAULT_TIMEOUT).raise_for_status()
    assert session.get(f"{base}/api/readings", timeout=DEFAULT_TIMEOUT).raise_for_status() is None


# --- 3. the timeout really fires --------------------------------------------


def test_a_read_timeout_fires_against_the_slow_endpoint(base, session):
    started = time.monotonic()
    with pytest.raises(requests.exceptions.Timeout):
        session.get(f"{base}/api/slow", params={"seconds": 3}, timeout=(3.05, 0.4))
    elapsed = time.monotonic() - started
    # It gave up on its own schedule, not the server's: well under 3 seconds.
    assert elapsed < 2.0


def test_a_timeout_is_a_requestexception_so_one_except_catches_the_family(base, session):
    with pytest.raises(requests.exceptions.RequestException):
        session.get(f"{base}/api/slow", params={"seconds": 3}, timeout=(3.05, 0.4))


# --- 4. retry with backoff --------------------------------------------------


def test_retry_succeeds_after_exactly_the_expected_number_of_attempts(base, session):
    session.get(f"{base}/control/reset", params={"fail": 2}, timeout=DEFAULT_TIMEOUT)
    sleeper = RecordingSleep()
    response = get_with_retry(
        f"{base}/api/flaky", session=session, attempts=4, sleep=sleeper, jitter=lambda: 1.0
    )
    assert response.status_code == 200
    assert response.json()["attempt"] == 3
    assert len(sleeper.waits) == 2


def test_the_retry_honours_retry_after_and_never_actually_sleeps(base, session):
    session.get(f"{base}/control/reset", params={"fail": 1}, timeout=DEFAULT_TIMEOUT)
    sleeper = RecordingSleep()
    started = time.monotonic()
    get_with_retry(f"{base}/api/flaky", session=session, attempts=3, sleep=sleeper, jitter=lambda: 1.0)
    assert sleeper.waits == [1.0]  # the server's Retry-After: 1
    assert time.monotonic() - started < 0.5


def test_retry_gives_up_and_says_how_many_attempts_it_made(base, session):
    session.get(f"{base}/control/reset", params={"fail": 99}, timeout=DEFAULT_TIMEOUT)
    sleeper = RecordingSleep()
    with pytest.raises(ReadingsUnavailable) as caught:
        get_with_retry(
            f"{base}/api/flaky", session=session, attempts=3, sleep=sleeper, jitter=lambda: 1.0
        )
    assert "after 3 attempts" in str(caught.value)
    assert len(sleeper.waits) == 2
    session.get(f"{base}/control/reset", params={"fail": 0}, timeout=DEFAULT_TIMEOUT)


def test_a_500_is_retried_and_a_404_is_not(base, session):
    assert 500 in RETRY_STATUSES and 429 in RETRY_STATUSES
    assert 404 not in RETRY_STATUSES and 400 not in RETRY_STATUSES and 401 not in RETRY_STATUSES
    sleeper = RecordingSleep()
    response = get_with_retry(
        f"{base}/api/missing", session=session, attempts=3, sleep=sleeper, jitter=lambda: 1.0
    )
    assert response.status_code == 404
    assert sleeper.waits == []  # returned on the first attempt, no waiting


@pytest.mark.parametrize(
    "attempts,expected",
    [(1, []), (2, [0.5]), (4, [0.5, 1.0, 2.0]), (6, [0.5, 1.0, 2.0, 4.0, 8.0])],
)
def test_the_backoff_schedule_doubles_and_caps(attempts, expected):
    assert backoff_delays(attempts, jitter=lambda: 1.0) == expected


def test_jitter_spreads_each_wait_over_half_its_slot():
    assert backoff_delays(4, jitter=lambda: 0.0) == [0.25, 0.5, 1.0]
    assert backoff_delays(4, jitter=lambda: 1.0) == [0.5, 1.0, 2.0]


# --- 5. Session and connection reuse ----------------------------------------


def test_one_session_reuses_one_connection_for_many_requests(base, server):
    before = server.connections
    with requests.Session() as pooled:
        for _ in range(5):
            pooled.get(f"{base}/api/readings", timeout=DEFAULT_TIMEOUT).close()
    assert server.connections - before == 1


def test_requests_get_without_a_session_opens_a_connection_every_time(base, server):
    before = server.connections
    for _ in range(5):
        requests.get(f"{base}/api/readings", timeout=DEFAULT_TIMEOUT).close()
    assert server.connections - before == 5


def test_the_session_carries_shared_headers_to_every_request(base, session):
    echoed = session.post(f"{base}/api/echo", json={"hello": "world"}, timeout=DEFAULT_TIMEOUT)
    assert echoed.status_code == 201
    assert echoed.json()["user_agent"].startswith("day078-lab/1.0")
    assert echoed.json()["content_type"] == "application/json"
    assert echoed.json()["json"] == {"hello": "world"}


def test_no_authorization_header_is_sent_when_the_environment_has_no_token(
    base, session, monkeypatch
):
    monkeypatch.delenv("READINGS_TOKEN", raising=False)
    echoed = session.post(f"{base}/api/echo", json={}, timeout=DEFAULT_TIMEOUT)
    assert echoed.json()["authorization_seen"] is False


def test_a_token_in_the_environment_becomes_an_authorization_header(base, monkeypatch):
    monkeypatch.setenv("READINGS_TOKEN", "not-a-real-secret")
    with make_session() as tokened:
        echoed = tokened.post(f"{base}/api/echo", json={}, timeout=DEFAULT_TIMEOUT)
    assert echoed.json()["authorization_seen"] is True


# --- 6. redirects -----------------------------------------------------------


def test_a_301_is_followed_by_default_and_recorded_in_history(base, session):
    response = session.get(f"{base}/old/readings", timeout=DEFAULT_TIMEOUT)
    assert response.status_code == 200
    assert [r.status_code for r in response.history] == [301]


def test_allow_redirects_false_shows_the_301_and_its_location(base, session):
    response = session.get(f"{base}/old/readings", timeout=DEFAULT_TIMEOUT, allow_redirects=False)
    assert response.status_code == 301
    assert response.headers["Location"] == "/api/readings"
    assert response.history == []


# --- 7. streaming -----------------------------------------------------------


def test_streaming_writes_the_whole_body_in_many_small_chunks(base, session, tmp_path):
    destination = tmp_path / "large.txt"
    total, chunks, digest = stream_to_file(
        f"{base}/api/large?kb=512", str(destination), session=session, chunk_size=8192
    )
    assert total == 512 * 1024
    assert chunks == 64
    assert destination.stat().st_size == total
    assert len(digest) == 64


def test_the_chunk_size_decides_how_much_is_held_at_once(base, session, tmp_path):
    total, chunks, _ = stream_to_file(
        f"{base}/api/large?kb=64", str(tmp_path / "s.txt"), session=session, chunk_size=1024
    )
    assert (total, chunks) == (64 * 1024, 64)
