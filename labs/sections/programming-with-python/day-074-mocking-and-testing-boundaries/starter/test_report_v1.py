"""Exercises 1-2 — test `report_v1.write_daily_report` with `unittest.mock`.

Run these from the lab directory:

    .venv/bin/pytest starter/test_report_v1.py -q

`report_v1.py` is given to you complete and it is deliberately bad: it reads the
clock, calls the service and writes a file inside one function. There is no way
to test it without replacing those three things at run time, so that is what
this file does. Notice how much scaffolding one four-line function costs. That
feeling is the argument for exercise 3.

Delete the `raise NotImplementedError(...)` line from each exercise as you
complete it.
"""

import datetime
from unittest.mock import patch

import report_v1

FIXED_DAY = datetime.date(2026, 4, 12)
READINGS = [12.0, 14.0, 20.0, 22.0] * 6  # 24 values; the mean is exactly 17.0

EXPECTED_FILE = (
    "station ALPHA — 2026-04-12\n"
    "  readings 24\n"
    "  minimum  12.0\n"
    "  maximum  22.0\n"
    "  mean     17.0\n"
)


def test_summarise_needs_no_patching():
    """Exercise 1 — the part that was already testable.

    `summarise` takes its input as an argument, so it has no boundary. Assert
    that `report_v1.summarise(READINGS)` returns the dict with count 24,
    minimum 12.0, maximum 22.0 and mean 17.0.

    Replace the line below with your assertion.
    """
    raise NotImplementedError("Exercise 1: assert on report_v1.summarise(READINGS)")


def test_write_daily_report_writes_the_expected_file(tmp_path):
    """Exercise 2 — the part that needs two patches and a temporary directory.

    Steps:

      a. Patch the NETWORK. `report_v1.py` says
         `from sensor_service import fetch_readings`, so the name to replace is
         `report_v1.fetch_readings` — where it is LOOKED UP, not where it was
         defined. Give it `return_value=READINGS` and keep the handle so you can
         assert on it.
      b. Patch the CLOCK. `report_v1.py` says `import datetime`, so the name it
         looks up is `report_v1.datetime`. Patch that and set
         `fake_datetime.date.today.return_value = FIXED_DAY`.
      c. Call `report_v1.write_daily_report("ALPHA", str(tmp_path))` inside the
         `with` block. `tmp_path` is a pytest fixture (Day 72) giving you a
         fresh directory that pytest cleans up.
      d. After the block, assert three things: the fetch handle was called once
         with `("ALPHA", "2026-04-12")`; the returned path is named
         `ALPHA-2026-04-12.txt`; and its text equals `EXPECTED_FILE`.

    A skeleton to fill in:

        with (
            patch("report_v1.fetch_readings", return_value=READINGS) as fetch,
            patch("report_v1.datetime") as fake_datetime,
        ):
            ...

    Replace the line below with your test.
    """
    raise NotImplementedError("Exercise 2: patch the clock and the service, then assert")


def test_the_wrong_patch_target_does_nothing(tmp_path):
    """Exercise 2b — prove the rule to yourself, once.

    Copy your exercise-2 test, change the first patch target from
    `"report_v1.fetch_readings"` to `"sensor_service.fetch_readings"`, and run
    it. It will take about half a second and then fail (or raise
    `ServiceError`), because `report_v1` holds its own reference to the function
    and never looks at `sensor_service` again.

    Once you have SEEN that, make this test assert the reason, instantly and
    without touching the service. Inside
    `with patch("sensor_service.fetch_readings") as replaced:` assert that
    `sensor_service.fetch_readings is replaced` (the patch worked) while
    `report_v1.fetch_readings is not replaced` (it reached nobody). Import
    `sensor_service` at the top of the file to do this.

    Replace the line below with those two assertions.
    """
    raise NotImplementedError("Exercise 2b: show that the wrong target changes nothing")
