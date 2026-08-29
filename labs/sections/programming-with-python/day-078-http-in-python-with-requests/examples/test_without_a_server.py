"""The Day 74 payoff: the same client, tested with NO server at all.

Not a local server. Not a mock of `requests`. Not a patch. A forty-line
fake object passed in through the `session=` parameter that was put there
for exactly this purpose.

Every test in this file runs in microseconds, would run identically on a
machine with no network stack, and can produce a ConnectionError, a 429
storm or a malformed body on demand — states that are awkward to arrange
even against a server you control.

The one thing these tests CANNOT prove is that your understanding of the
real server is correct. That is what `test_client.py` is for. Keep both.
"""

from __future__ import annotations

import pytest
import requests

from client import (
    Reading,
    ReadingsUnavailable,
    StationNotFound,
    fetch_readings,
    get_with_retry,
    summarise,
)
from fake_session import FakeResponse, FakeSession

PAYLOAD = {
    "station": "ALPHA",
    "count": 2,
    "readings": [
        {"station": "ALPHA", "hour": 0, "celsius": 12.0},
        {"station": "ALPHA", "hour": 12, "celsius": 22.0},
    ],
}


class RecordingSleep:
    def __init__(self) -> None:
        self.waits: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.waits.append(round(seconds, 4))


def test_fetch_readings_works_against_a_fake_session():
    session = FakeSession([FakeResponse(200, PAYLOAD)])
    assert fetch_readings("http://example.invalid", "ALPHA", session=session) == [
        Reading("ALPHA", 0, 12.0),
        Reading("ALPHA", 12, 22.0),
    ]


def test_the_url_and_params_the_client_would_have_sent():
    session = FakeSession([FakeResponse(200, PAYLOAD)])
    fetch_readings("http://example.invalid", "ALPHA", session=session)
    call = session.calls[0]
    assert call["url"] == "http://example.invalid/api/readings"
    assert call["params"] == {"station": "ALPHA"}


def test_every_call_carries_a_timeout():
    """The check worth having in a real codebase. A missing timeout hangs."""
    session = FakeSession([FakeResponse(200, PAYLOAD)])
    fetch_readings("http://example.invalid", "ALPHA", session=session)
    assert session.timeouts == [(3.05, 10.0)]
    assert all(t is not None for t in session.timeouts)


def test_a_404_becomes_a_domain_exception_with_no_server_involved():
    session = FakeSession([FakeResponse(404, {"error": "not_found"})])
    with pytest.raises(StationNotFound):
        fetch_readings("http://example.invalid", "GHOST", session=session)


def test_a_connection_error_can_be_produced_on_demand():
    session = FakeSession([requests.exceptions.ConnectionError("name resolution failed")])
    with pytest.raises(requests.exceptions.ConnectionError):
        fetch_readings("http://example.invalid", "ALPHA", session=session)


def test_retry_recovers_from_two_429s_and_never_waits():
    session = FakeSession(
        [
            FakeResponse(429, {"error": "rate_limited"}, {"Retry-After": "2"}),
            FakeResponse(429, {"error": "rate_limited"}, {"Retry-After": "2"}),
            FakeResponse(200, PAYLOAD),
        ]
    )
    sleeper = RecordingSleep()
    response = get_with_retry(
        "http://example.invalid/api/flaky",
        session=session,
        attempts=4,
        sleep=sleeper,
        jitter=lambda: 1.0,
    )
    assert response.status_code == 200
    assert len(session.calls) == 3
    assert sleeper.waits == [2.0, 2.0]


def test_retry_survives_a_transport_failure_then_succeeds():
    session = FakeSession(
        [requests.exceptions.ConnectTimeout("no route"), FakeResponse(200, PAYLOAD)]
    )
    sleeper = RecordingSleep()
    response = get_with_retry(
        "http://example.invalid/api/flaky",
        session=session,
        attempts=3,
        sleep=sleeper,
        jitter=lambda: 1.0,
    )
    assert response.status_code == 200
    assert sleeper.waits == [0.5]


def test_retry_gives_up_after_five_503s_and_names_the_count():
    session = FakeSession([FakeResponse(503, {"error": "unavailable"}) for _ in range(5)])
    sleeper = RecordingSleep()
    with pytest.raises(ReadingsUnavailable) as caught:
        get_with_retry(
            "http://example.invalid/api/flaky",
            session=session,
            attempts=5,
            sleep=sleeper,
            jitter=lambda: 1.0,
        )
    assert "after 5 attempts" in str(caught.value)
    assert sleeper.waits == [0.5, 1.0, 2.0, 4.0]


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 422])
def test_a_client_error_is_returned_immediately_and_never_retried(status):
    session = FakeSession([FakeResponse(status, {"error": "no"})])
    sleeper = RecordingSleep()
    response = get_with_retry(
        "http://example.invalid/api/x",
        session=session,
        attempts=4,
        sleep=sleeper,
        jitter=lambda: 1.0,
    )
    assert response.status_code == status
    assert len(session.calls) == 1
    assert sleeper.waits == []


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
def test_a_retryable_status_is_tried_again(status):
    session = FakeSession([FakeResponse(status, {"error": "later"}), FakeResponse(200, PAYLOAD)])
    get_with_retry(
        "http://example.invalid/api/x",
        session=session,
        attempts=3,
        sleep=RecordingSleep(),
        jitter=lambda: 1.0,
    )
    assert len(session.calls) == 2


def test_summarise_is_pure_and_needs_no_session_at_all():
    assert summarise([Reading("A", 0, 10.0), Reading("A", 1, 20.0)])["mean"] == 15.0
