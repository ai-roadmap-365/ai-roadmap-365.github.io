"""Version 1 — every boundary hard-coded. This is the "before" picture.

`write_daily_report` does four things, and only one of them is logic:

  1. reads the CLOCK          `datetime.date.today()`
  2. calls the NETWORK        `fetch_readings(...)`
  3. computes the summary     <- the only part worth testing
  4. writes the FILESYSTEM    `Path(...).write_text(...)`

There is no way to test step 3 without also performing steps 1, 2 and 4,
because they are welded into the same function. That is what makes this
version untestable without patching.

Note the import style on the next line. `from sensor_service import
fetch_readings` binds the name `fetch_readings` **into this module**. That
single detail decides which patch target works, and it is the thing that trips
everybody up the first time.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from sensor_service import fetch_readings


def summarise(readings: list[float]) -> dict[str, float | int]:
    """Reduce a day of readings to the four numbers the report shows.

    Pure: no clock, no network, no filesystem. Give it a list, get a dict.
    """
    if not readings:
        raise ValueError("cannot summarise an empty day of readings")
    return {
        "count": len(readings),
        "minimum": min(readings),
        "maximum": max(readings),
        "mean": round(sum(readings) / len(readings), 1),
    }


def render(station: str, day: datetime.date, summary: dict[str, float | int]) -> str:
    """Format one report. Also pure."""
    return "\n".join(
        [
            f"station {station} — {day.isoformat()}",
            f"  readings {summary['count']}",
            f"  minimum  {summary['minimum']:.1f}",
            f"  maximum  {summary['maximum']:.1f}",
            f"  mean     {summary['mean']:.1f}",
        ]
    )


def write_daily_report(station: str, out_dir: str) -> Path:
    """Fetch today's readings for one station and write the report to a file.

    Four responsibilities, three of them boundaries. Every test of the third
    one has to pay for the other three.
    """
    day = datetime.date.today()
    readings = fetch_readings(station, day.isoformat())
    body = render(station, day, summarise(readings))
    path = Path(out_dir) / f"{station}-{day.isoformat()}.txt"
    path.write_text(body + "\n", encoding="utf-8")
    return path
