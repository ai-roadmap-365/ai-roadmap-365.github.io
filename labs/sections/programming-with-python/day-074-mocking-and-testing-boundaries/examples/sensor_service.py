"""A stand-in for a remote sensor service — the "world" this lab must not reach.

Nothing in this file opens a socket, resolves a hostname, or contacts anything.
It exists to be **slow** and **non-deterministic** on purpose, because that is
exactly what a real network call is, and it is the whole reason a unit test
must never reach through a boundary like this one.

Read the two constants below as the definition of a bad test dependency:

    LATENCY_SECONDS = 0.4   ->  a suite of 200 tests would take 80 seconds
    FAILURE_RATE    = 0.25  ->  one test run in four fails for no good reason

A real HTTP client has the same two properties, plus a third: it costs money
when the thing on the other end is a metered API.
"""

from __future__ import annotations

import random
import time

#: How long the "service" pretends to take. A local network round trip is a few
#: milliseconds; a cross-continent HTTPS call is often a few hundred.
LATENCY_SECONDS = 0.4

#: How often the "service" pretends to be unavailable.
FAILURE_RATE = 0.25

#: How many hourly readings a successful call returns.
READINGS_PER_DAY = 24


class ServiceError(Exception):
    """The service was reachable but could not answer the question."""


def fetch_readings(station: str, day: str) -> list[float]:
    """Return one temperature reading per hour for ``station`` on ``day``.

    Slow every time, and unavailable roughly a quarter of the time. The values
    are random, so no test can assert anything about them.
    """
    time.sleep(LATENCY_SECONDS)
    if random.random() < FAILURE_RATE:
        raise ServiceError(f"station {station!r} did not answer for {day}")
    return [round(random.uniform(-4.0, 31.0), 1) for _ in range(READINGS_PER_DAY)]
