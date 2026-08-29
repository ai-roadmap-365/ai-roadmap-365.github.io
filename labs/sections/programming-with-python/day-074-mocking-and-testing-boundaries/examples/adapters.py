"""The adapter ring for `report_v2.py` — everything that touches the world.

Three adapters, one per boundary the core refuses to own:

  * `system_clock`      the clock
  * `LiveSensorClient`  the network (here, the stand-in service)
  * `write_report`      the filesystem

Each is a handful of lines with no branching worth testing, which is the point.
The logic lives in the core, where it can be tested for free; the risk lives
out here, where there is almost nothing to get wrong.
"""

from __future__ import annotations

import datetime
import time
from pathlib import Path

from report_v2 import DailyReport, ReadingsUnavailable
from sensor_client import SensorClient
from sensor_service import ServiceError


def system_clock() -> datetime.date:
    """The real clock. The only place in the program that reads today's date."""
    return datetime.date.today()


class LiveSensorClient:
    """Wraps the real client and translates its failure into a domain error.

    This translation is the reason the core never imports `sensor_service`. A
    second client for a different vendor would translate that vendor's errors
    the same way, and `build_report` would not change by a character.
    """

    def __init__(self, client: SensorClient | None = None) -> None:
        self._client = client or SensorClient()

    def fetch_readings(self, station: str, day: str) -> list[float]:
        try:
            return self._client.fetch_readings(station, day)
        except ServiceError as exc:
            raise ReadingsUnavailable(str(exc)) from exc


def write_report(report: DailyReport, out_dir: str) -> Path:
    """Write a finished report to disk. Formatting already happened in the core."""
    path = Path(out_dir) / report.filename()
    path.write_text(report.render() + "\n", encoding="utf-8")
    return path


def real_sleep(seconds: float) -> None:
    """The real backoff. Injected so tests can pass something instantaneous."""
    time.sleep(seconds)
