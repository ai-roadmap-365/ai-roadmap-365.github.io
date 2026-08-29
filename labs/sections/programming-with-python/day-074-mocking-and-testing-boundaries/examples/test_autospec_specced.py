"""The same test, written against a specced double. It FAILS, and it is right.

Run it on its own to watch it catch the bug:

    pytest examples/test_autospec_specced.py -q

`create_autospec(SensorClient, instance=True)` builds a double that has exactly
the methods `SensorClient` has, with exactly their signatures. There is no
`fetch_radings` on it, so the test cannot stub one, and the call inside
`latest_average` raises `AttributeError` at the moment the bug happens.

This file is EXPECTED to fail. The lab's test suite asserts that it does — a
suite that could not tell these two files apart would be proving nothing.
"""

from unittest.mock import create_autospec

from sensor_client import SensorClient
from typo_under_test import latest_average


def test_latest_average_with_an_autospecced_double():
    client = create_autospec(SensorClient, instance=True)
    client.fetch_readings.return_value = [10.0, 20.0, 30.0]

    assert latest_average(client, "ALPHA", "2026-04-12") == 20.0


def test_a_specced_double_refuses_the_misspelled_name():
    client = create_autospec(SensorClient, instance=True)

    # This is the line that a bare Mock() would have accepted in silence.
    client.fetch_radings.return_value = [1.0]
