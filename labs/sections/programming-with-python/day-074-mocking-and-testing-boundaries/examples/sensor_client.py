"""The object-shaped version of the same boundary.

`report_v2.py` accepts any object with a `fetch_readings(station, day)` method.
This is the real one — it delegates to the slow, flaky stand-in service. It is
also the class used to demonstrate `spec=` and `autospec=`: a test double built
from this class knows which methods exist and what arguments they take, and a
double built from nothing at all knows neither.
"""

from __future__ import annotations

from sensor_service import ServiceError, fetch_readings

__all__ = ["SensorClient", "ServiceError"]


class SensorClient:
    """A client for the sensor service."""

    def __init__(self, base_url: str = "sensors.internal", timeout: float = 5.0) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def fetch_readings(self, station: str, day: str) -> list[float]:
        """Return one reading per hour for ``station`` on ``day`` (ISO date)."""
        return fetch_readings(station, day)

    def stations(self) -> list[str]:
        """Return the station identifiers this client can query."""
        return ["ALPHA", "BRAVO", "CHARLIE"]
