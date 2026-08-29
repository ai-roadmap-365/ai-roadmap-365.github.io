"""Production code with a real bug in it. Read the call carefully.

`SensorClient` has a method called `fetch_readings`. The line below calls
`fetch_radings`. Against the real client that is an `AttributeError` on the
first request in production.

The point of this file is what happens in the *test*: a plain `Mock()` accepts
`fetch_radings` happily, invents an attribute for it, and lets a test that
copies the typo pass. A double built with `spec=` or `create_autospec` knows
which methods the real class has, and refuses.
"""

from __future__ import annotations


def latest_average(client, station: str, day: str) -> float:
    """Return the mean reading for one station on one day."""
    readings = client.fetch_radings(station, day)
    return round(sum(readings) / len(readings), 1)
