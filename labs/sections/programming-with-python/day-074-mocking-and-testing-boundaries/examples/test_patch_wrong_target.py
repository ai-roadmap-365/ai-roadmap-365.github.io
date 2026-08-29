"""The same test with the patch aimed at the WRONG target. It FAILS.

    pytest examples/test_patch_wrong_target.py -q

The only difference from `test_patch_right_target.py` is one string:

    patch("sensor_service.fetch_readings")   <- where the function was DEFINED
    patch("report_v1.fetch_readings")        <- where the name is LOOKED UP

`report_v1` did `from sensor_service import fetch_readings` at import time, so
it holds its own reference. Rebinding the attribute on `sensor_service` after
that point changes nothing `report_v1` can see: the real, slow, random function
is called, and the assertion about the file contents fails (or the real service
raises `ServiceError` first — either way the test does not pass).

This file is EXPECTED to fail. The lab's test suite asserts that it does.
"""

import datetime
from unittest.mock import patch

import report_v1

FIXED_DAY = datetime.date(2026, 4, 12)
READINGS = [12.0, 14.0, 20.0, 22.0] * 6


def test_write_daily_report_with_the_wrong_patch_target(tmp_path):
    with (
        patch("sensor_service.fetch_readings", return_value=READINGS),
        patch("report_v1.datetime") as fake_datetime,
    ):
        fake_datetime.date.today.return_value = FIXED_DAY
        path = report_v1.write_daily_report("ALPHA", str(tmp_path))

    assert path.read_text(encoding="utf-8") == (
        "station ALPHA — 2026-04-12\n"
        "  readings 24\n"
        "  minimum  12.0\n"
        "  maximum  22.0\n"
        "  mean     17.0\n"
    )
