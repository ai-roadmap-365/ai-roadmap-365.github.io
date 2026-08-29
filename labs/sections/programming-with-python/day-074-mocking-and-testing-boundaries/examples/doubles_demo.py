"""The five kinds of test double, each demonstrated in a few real lines.

    python3 examples/doubles_demo.py

Gerard Meszaros named these five in *xUnit Test Patterns* (2007). Everyday
speech collapses all of them into the word "mock", which is why so many
conversations about mocking go nowhere: two people say "mock" and mean a stub
and a spy. The names are worth keeping because they answer different questions.
"""

from __future__ import annotations

import datetime
from unittest.mock import Mock, create_autospec

from fakes import (
    DummyClient,
    FakeSensorClient,
    RecordingSleep,
    SpyClock,
    StubSensorClient,
    frozen_clock,
)
from report_v2 import ReadingsUnavailable, build_report
from sensor_client import SensorClient

DAY = datetime.date(2026, 4, 12)
READINGS = [12.0, 14.0, 20.0, 22.0] * 6


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("The five test doubles, on one program")
    print("=" * 38)

    rule("1. DUMMY — fills an argument slot, must never be used")
    try:
        build_report("ALPHA", clock=frozen_clock(DAY), client=DummyClient(), attempts=0)
    except Exception as exc:
        print(f"  build_report(attempts=0) -> {type(exc).__name__}: {exc}")
    print("  the dummy was never called, which is what proves the early exit")

    rule("2. STUB — a canned answer, no questions asked, nothing recorded")
    stub = StubSensorClient(READINGS)
    report = build_report("ALPHA", clock=frozen_clock(DAY), client=stub)
    print(f"  StubSensorClient -> mean {report.mean}")
    print(f"  frozen_clock({DAY}) -> {frozen_clock(DAY)()}")

    rule("3. SPY — answers like a stub AND records how it was used")
    clock = SpyClock(DAY)
    waits = RecordingSleep()
    client = FakeSensorClient([ReadingsUnavailable("timeout"), READINGS])
    build_report("ALPHA", clock=clock, client=client, attempts=2, sleep=waits)
    print(f"  the clock was read {clock.calls} time(s)")
    print(f"  the backoff was asked to wait {waits.waits} second(s) — and waited none")

    rule("4. MOCK — a double with an EXPECTATION built into it")
    mock_client = create_autospec(SensorClient, instance=True)
    mock_client.fetch_readings.return_value = READINGS
    build_report("BRAVO", clock=frozen_clock(DAY), client=mock_client)
    mock_client.fetch_readings.assert_called_once_with("BRAVO", "2026-04-12")
    print("  assert_called_once_with('BRAVO', '2026-04-12') -> satisfied")
    print(f"  call_args: {mock_client.fetch_readings.call_args}")
    try:
        mock_client.fetch_readings.assert_called_once_with("CHARLIE", "2026-04-12")
    except AssertionError as exc:
        first_line = str(exc).splitlines()[0]
        print(f"  the same assertion with the wrong station -> AssertionError: {first_line}")

    rule("5. FAKE — a working implementation, simplified")
    fake = FakeSensorClient([ReadingsUnavailable("timeout"), READINGS])
    report = build_report("CHARLIE", clock=frozen_clock(DAY), client=fake, attempts=2)
    print(f"  report mean {report.mean}, calls recorded {fake.calls}")
    print("  one fake answered the stub question AND the spy question AND the mock question")

    rule("The colloquial 'mock' — what unittest.mock actually gives you")
    m = Mock()
    print(f"  Mock() is a stub when you set return_value : {Mock(return_value=7)()}")
    m.side_effect = [1, 2, 3]
    print(f"  ...a sequence when you set side_effect      : {m()}, {m()}, {m()}")
    boom = Mock(side_effect=ReadingsUnavailable("timeout"))
    try:
        boom()
    except ReadingsUnavailable as exc:
        print(f"  ...an error raiser with side_effect=exc     : {type(exc).__name__}: {exc}")
    print("  ...a spy, because every call is recorded, always")
    print("  ...and a mock, the moment you call an assert_ method on it")


if __name__ == "__main__":
    main()
