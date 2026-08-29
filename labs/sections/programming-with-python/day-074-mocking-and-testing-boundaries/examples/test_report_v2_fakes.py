"""Testing report_v2 with hand-written fakes. No patching anywhere.

    pytest examples/test_report_v2_fakes.py -q

Compare this file with `test_patch_right_target.py`. There are no `patch`
calls, no module objects replaced, no `tmp_path`, and nothing to undo. The
boundaries are parameters, so a test simply passes different arguments — which
is what "dependency injection" means once you strip the phrase of ceremony.

Every test here runs in microseconds and gives the same answer on every machine
on every day, because nothing in the code under test can reach a clock, a
network, a disk, or a random number generator.
"""

import datetime

import pytest
from fakes import (
    DummyClient,
    FakeSensorClient,
    RecordingSleep,
    SpyClock,
    StubSensorClient,
    frozen_clock,
)
from report_v2 import (
    DailyReport,
    ReadingsUnavailable,
    ReportError,
    ReportUnavailable,
    build_report,
    summarise,
)

DAY = datetime.date(2026, 4, 12)
READINGS = [12.0, 14.0, 20.0, 22.0] * 6  # 24 values, mean exactly 17.0


def test_summarise_reduces_a_day_to_four_numbers():
    report = summarise("ALPHA", DAY, READINGS)
    assert report == DailyReport("ALPHA", DAY, 24, 12.0, 22.0, 17.0)


def test_summarise_refuses_an_empty_day():
    with pytest.raises(ReportError, match="empty day"):
        summarise("ALPHA", DAY, [])


def test_build_report_uses_the_injected_clock_and_client():
    client = StubSensorClient(READINGS)
    report = build_report("ALPHA", clock=frozen_clock(DAY), client=client)
    assert report.day == DAY
    assert report.mean == 17.0
    assert report.render().splitlines()[0] == "station ALPHA — 2026-04-12"


def test_the_client_is_asked_for_the_clock_s_day():
    # A fake records its calls, so it answers the question a spy would answer.
    client = FakeSensorClient([READINGS])
    build_report("BRAVO", clock=frozen_clock(DAY), client=client)
    assert client.calls == [("BRAVO", "2026-04-12")]


def test_the_clock_is_read_exactly_once_per_report():
    # A report that straddled midnight would be half yesterday and half today.
    clock = SpyClock(DAY)
    build_report("ALPHA", clock=clock, client=StubSensorClient(READINGS))
    assert clock.calls == 1


def test_a_transient_failure_is_retried_and_then_succeeds():
    client = FakeSensorClient(
        [ReadingsUnavailable("timeout"), ReadingsUnavailable("timeout"), READINGS]
    )
    report = build_report("ALPHA", clock=frozen_clock(DAY), client=client, attempts=3)
    assert report.mean == 17.0
    assert len(client.calls) == 3


def test_backoff_grows_between_attempts_without_anyone_waiting():
    # The spy proves the backoff schedule. The suite still finishes instantly,
    # because the thing that would have slept is a list append.
    waits = RecordingSleep()
    client = FakeSensorClient(
        [ReadingsUnavailable("timeout"), ReadingsUnavailable("timeout"), READINGS]
    )
    build_report(
        "ALPHA",
        clock=frozen_clock(DAY),
        client=client,
        attempts=3,
        sleep=waits,
        backoff_seconds=0.5,
    )
    assert waits.waits == [0.5, 1.0]


def test_exhausting_every_attempt_raises_a_domain_error():
    client = FakeSensorClient([ReadingsUnavailable("timeout")] * 3)
    with pytest.raises(ReportUnavailable, match="after 3 attempts"):
        build_report("ALPHA", clock=frozen_clock(DAY), client=client, attempts=3)


def test_no_waiting_happens_when_the_first_attempt_succeeds():
    waits = RecordingSleep()
    build_report(
        "ALPHA", clock=frozen_clock(DAY), client=StubSensorClient(READINGS), sleep=waits
    )
    assert waits.waits == []


def test_a_bad_attempts_argument_is_refused_before_anything_is_called():
    # The dummy proves the client is never reached on this path: if it were,
    # the dummy would raise AssertionError instead of ReportError.
    with pytest.raises(ReportError, match="attempts must be at least 1"):
        build_report("ALPHA", clock=frozen_clock(DAY), client=DummyClient(), attempts=0)
