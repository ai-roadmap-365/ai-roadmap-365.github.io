"""YOUR FILE — exercise 7, plus the checks that grade exercises 1 to 6.

Run it at any time:

    .venv/bin/pytest starter -q

Every test for an unfinished exercise is SKIPPED, so this file exits 0 from
the first minute and turns green one exercise at a time. The skip is
decided by reading your `client.py`: as soon as a function no longer says
`raise NotImplementedError`, its tests start running.

The last section is exercise 7, and it is the point of the whole lab.
"""

from __future__ import annotations

import inspect
import time

import pytest
import requests

import client
from fake_session import FakeResponse, FakeSession


def unfinished(fn) -> bool:
    """True while `fn` still contains its `raise NotImplementedError` line."""
    try:
        return "raise NotImplementedError" in inspect.getsource(fn)
    except OSError:  # pragma: no cover - source always available here
        return False


def needs(fn):
    return pytest.mark.skipif(unfinished(fn), reason=f"{fn.__name__} is not written yet")


class RecordingSleep:
    """A spy from Day 74: it records what it was asked to wait, and waits 0."""

    def __init__(self) -> None:
        self.waits: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.waits.append(round(seconds, 4))


@pytest.fixture
def session():
    """A plain Session while exercise 5 is unfinished; yours once it is."""
    s = requests.Session() if unfinished(client.make_session) else client.make_session()
    yield s
    s.close()


# --- provided, and already passing: proof the server is up ------------------


def test_the_local_test_server_answers(base):
    """This one is written for you. If it fails, nothing else will work."""
    response = requests.get(f"{base}/api/readings", timeout=(3.05, 10.0))
    assert response.status_code == 200
    assert response.json()["count"] == 6


# --- exercise 1 -------------------------------------------------------------


@needs(client.fetch_readings)
def test_fetch_readings_parses_four_rows(base, session):
    readings = client.fetch_readings(base, "ALPHA", session=session)
    assert len(readings) == 4
    assert readings[0] == client.Reading("ALPHA", 0, 12.0)
    assert client.summarise(readings)["mean"] == 17.0


@needs(client.fetch_readings)
def test_fetch_readings_uses_params_so_the_value_is_encoded(base, session):
    awkward = "ALPHA ONE&station=BRAVO"
    echoed = session.get(f"{base}/api/search", params={"station": awkward}, timeout=(3.05, 10.0))
    assert echoed.json()["parsed"]["station"] == [awkward], (
        "if this fails you concatenated the query string instead of using params="
    )


# --- exercise 2 -------------------------------------------------------------


@needs(client.fetch_readings)
def test_an_unknown_station_raises_your_exception_not_a_traceback(base, session):
    with pytest.raises(client.StationNotFound) as caught:
        client.fetch_readings(base, "NOWHERE", session=session)
    assert "NOWHERE" in str(caught.value)


@needs(client.describe_failure)
def test_describe_failure_formats_a_404_and_a_500(base, session):
    missing = session.get(f"{base}/api/missing", timeout=(3.05, 10.0))
    assert client.describe_failure(missing) == (
        "HTTP 404 (your request was rejected) — no such station"
    )
    broken = session.get(f"{base}/api/broken", timeout=(3.05, 10.0))
    assert client.describe_failure(broken) == "HTTP 500 (the server failed) — the server fell over"


# --- exercise 3 -------------------------------------------------------------


@needs(client.backoff_delays)
def test_the_schedule_doubles_caps_and_jitters():
    assert client.backoff_delays(1, jitter=lambda: 1.0) == []
    assert client.backoff_delays(4, jitter=lambda: 1.0) == [0.5, 1.0, 2.0]
    assert client.backoff_delays(6, jitter=lambda: 1.0) == [0.5, 1.0, 2.0, 4.0, 8.0]
    assert client.backoff_delays(4, jitter=lambda: 0.0) == [0.25, 0.5, 1.0]
    with pytest.raises(ValueError):
        client.backoff_delays(0)


# --- exercise 4 -------------------------------------------------------------


@needs(client.get_with_retry)
def test_retry_recovers_from_two_429s_on_the_third_attempt(base, session):
    session.get(f"{base}/control/reset", params={"fail": 2}, timeout=(3.05, 10.0))
    sleeper = RecordingSleep()
    started = time.monotonic()
    response = client.get_with_retry(
        f"{base}/api/flaky", session=session, attempts=4, sleep=sleeper, jitter=lambda: 1.0
    )
    assert response.status_code == 200
    assert response.json()["attempt"] == 3
    assert len(sleeper.waits) == 2
    assert time.monotonic() - started < 0.5, "nothing should really have slept"


@needs(client.get_with_retry)
def test_retry_gives_up_and_names_the_attempt_count(base, session):
    session.get(f"{base}/control/reset", params={"fail": 99}, timeout=(3.05, 10.0))
    with pytest.raises(client.ReadingsUnavailable) as caught:
        client.get_with_retry(
            f"{base}/api/flaky", session=session, attempts=3, sleep=RecordingSleep(),
            jitter=lambda: 1.0,
        )
    assert "after 3 attempts" in str(caught.value)
    session.get(f"{base}/control/reset", params={"fail": 0}, timeout=(3.05, 10.0))


@needs(client.get_with_retry)
def test_a_404_is_returned_at_once_and_never_retried(base, session):
    sleeper = RecordingSleep()
    response = client.get_with_retry(
        f"{base}/api/missing", session=session, attempts=4, sleep=sleeper, jitter=lambda: 1.0
    )
    assert response.status_code == 404
    assert sleeper.waits == []


# --- exercise 5 -------------------------------------------------------------


@needs(client.make_session)
def test_the_session_sends_your_user_agent_and_no_token_by_default(base, monkeypatch):
    monkeypatch.delenv("READINGS_TOKEN", raising=False)
    with client.make_session() as s:
        echoed = s.post(f"{base}/api/echo", json={}, timeout=(3.05, 10.0))
    assert echoed.json()["user_agent"].startswith("day078-")
    assert echoed.json()["authorization_seen"] is False


@needs(client.make_session)
def test_a_token_in_the_environment_becomes_an_authorization_header(base, monkeypatch):
    monkeypatch.setenv("READINGS_TOKEN", "not-a-real-secret")
    with client.make_session() as s:
        echoed = s.post(f"{base}/api/echo", json={}, timeout=(3.05, 10.0))
    assert echoed.json()["authorization_seen"] is True


@needs(client.make_session)
def test_one_session_opens_one_connection_for_five_requests(base, server):
    before = server.connections
    with client.make_session() as s:
        for _ in range(5):
            s.get(f"{base}/api/readings", timeout=(3.05, 10.0)).close()
    assert server.connections - before == 1
    before = server.connections
    for _ in range(5):
        requests.get(f"{base}/api/readings", timeout=(3.05, 10.0)).close()
    assert server.connections - before == 5


# --- exercise 6 -------------------------------------------------------------


@needs(client.stream_to_file)
def test_streaming_writes_512_kib_in_64_chunks(base, session, tmp_path):
    destination = tmp_path / "large.txt"
    total, chunks, digest = client.stream_to_file(
        f"{base}/api/large?kb=512", str(destination), session=session, chunk_size=8192
    )
    assert total == 512 * 1024
    assert chunks == 64
    assert destination.stat().st_size == total
    assert len(digest) == 64


# --- the timeout, which needs no exercise: it is one keyword ----------------


def test_a_timeout_really_fires_against_the_slow_endpoint(base, session):
    """Provided and already passing. Read it — this is the habit of the day."""
    started = time.monotonic()
    with pytest.raises(requests.exceptions.Timeout):
        session.get(f"{base}/api/slow", params={"seconds": 3}, timeout=(3.05, 0.4))
    assert time.monotonic() - started < 2.0


# --- exercise 7 — the payoff: tests with NO server at all -------------------
#
# `fake_session.FakeSession` is provided in examples/. Because every function
# in client.py takes `session` as a parameter, these tests need no server, no
# socket and no port. Write at least three more of your own below:
#
#   * one that proves a ConnectionError propagates (script the exception);
#   * one that proves a 503 is retried and a 403 is not;
#   * one that proves EVERY call your client makes carries a timeout.
#
# The last one is the check worth stealing for your real projects.


@needs(client.fetch_readings)
def test_fetch_readings_works_with_no_server_in_sight():
    """Provided, as the model for the ones you write."""
    payload = {"readings": [{"station": "ALPHA", "hour": 0, "celsius": 12.0}]}
    fake = FakeSession([FakeResponse(200, payload)])
    assert client.fetch_readings("http://example.invalid", "ALPHA", session=fake) == [
        client.Reading("ALPHA", 0, 12.0)
    ]
    assert fake.calls[0]["params"] == {"station": "ALPHA"}
    assert fake.timeouts == [(3.05, 10.0)], "every call must carry a timeout"
