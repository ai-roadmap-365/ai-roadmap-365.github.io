"""Why an un-specced Mock is dangerous — shown, not asserted.

    python3 examples/autospec_demo.py

A `Mock()` with no spec answers yes to every question. Ask it for a method that
does not exist and it invents one. Call a method with arguments the real object
would reject and it accepts them. Both behaviours make a test agree with
whatever the code under test happens to do, including the parts that are wrong.

`spec=` fixes the first. `autospec=` / `create_autospec` fixes both.
"""

from __future__ import annotations

from unittest.mock import Mock, create_autospec

from sensor_client import SensorClient
from typo_under_test import latest_average


def show(label: str, fn) -> None:
    try:
        print(f"  {label}\n      -> {fn()}")
    except Exception as exc:
        print(f"  {label}\n      -> {type(exc).__name__}: {exc}")


def main() -> None:
    print("An un-specced Mock accepts everything")
    print("=" * 37)
    print("The real class:")
    print(f"  SensorClient methods: {sorted(m for m in vars(SensorClient) if not m.startswith('_'))}")
    print("  fetch_readings(self, station: str, day: str) -> list[float]")
    print()

    bare = Mock()
    show("bare Mock: an attribute that does not exist", lambda: bare.fetch_radings)
    show(
        "bare Mock: a call with an argument the real method has never heard of",
        lambda: bare.fetch_readings("ALPHA", "2026-04-12", retries=3, nonsense=True),
    )
    show("bare Mock: what it recorded", lambda: bare.fetch_readings.call_args)

    print()
    specced = Mock(spec=SensorClient)
    show("Mock(spec=SensorClient): the misspelled attribute", lambda: specced.fetch_radings)
    show(
        "Mock(spec=SensorClient): but the SIGNATURE is still unchecked",
        lambda: specced.fetch_readings("ALPHA", "2026-04-12", retries=3),
    )

    print()
    auto = create_autospec(SensorClient, instance=True)
    show("create_autospec: the misspelled attribute", lambda: auto.fetch_radings)
    show("create_autospec: a missing argument", lambda: auto.fetch_readings("ALPHA"))
    show(
        "create_autospec: an argument that does not exist",
        lambda: auto.fetch_readings("ALPHA", "2026-04-12", retries=3),
    )
    auto.fetch_readings.return_value = [10.0, 20.0, 30.0]
    show("create_autospec: the call the real object would accept", lambda: auto.fetch_readings("ALPHA", "2026-04-12"))

    print()
    print("The bug this hides, in three lines")
    print("=" * 34)
    print("  typo_under_test.latest_average calls client.fetch_radings(...)")
    show("with a bare Mock (this is what the green test does)", lambda: latest_average(_stubbed_bare(), "ALPHA", "2026-04-12"))
    show("with create_autospec (this is what a good test does)", lambda: latest_average(_stubbed_auto(), "ALPHA", "2026-04-12"))
    show("with the REAL SensorClient (this is production)", lambda: latest_average(SensorClient(), "ALPHA", "2026-04-12"))


def _stubbed_bare() -> Mock:
    client = Mock()
    client.fetch_radings.return_value = [10.0, 20.0, 30.0]
    return client


def _stubbed_auto():
    client = create_autospec(SensorClient, instance=True)
    client.fetch_readings.return_value = [10.0, 20.0, 30.0]
    return client


if __name__ == "__main__":
    main()
