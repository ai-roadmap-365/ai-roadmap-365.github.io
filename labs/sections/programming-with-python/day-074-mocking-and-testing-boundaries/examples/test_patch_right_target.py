"""Testing report_v1 with `patch`, aimed at the RIGHT target. It passes.

    pytest examples/test_patch_right_target.py -q

`report_v1.py` says `from sensor_service import fetch_readings`, which binds the
name into `report_v1`'s own namespace at import time. So the name to replace is
`report_v1.fetch_readings` — where it is LOOKED UP, not where it was defined.

Read what it takes to test one four-line function: two patches, a stubbed
module object, a temporary directory, and a comment explaining the second
patch. Every line of that is the price of the boundaries being hard-coded. The
same behaviour in `report_v2.py` needs none of it.
"""

import datetime
from unittest.mock import patch

import report_v1

FIXED_DAY = datetime.date(2026, 4, 12)
READINGS = [12.0, 14.0, 20.0, 22.0] * 6  # 24 values, mean exactly 17.0


def test_write_daily_report_writes_the_expected_file(tmp_path):
    # Patch 1: the network, at the name report_v1 looks up.
    # Patch 2: the clock. report_v1 says `import datetime`, so the whole module
    # object is what it looks up — replacing it wholesale is ugly, and the
    # ugliness is a message about the design, not about unittest.mock.
    with (
        patch("report_v1.fetch_readings", return_value=READINGS) as fetch,
        patch("report_v1.datetime") as fake_datetime,
    ):
        fake_datetime.date.today.return_value = FIXED_DAY
        path = report_v1.write_daily_report("ALPHA", str(tmp_path))

    fetch.assert_called_once_with("ALPHA", "2026-04-12")
    assert path.name == "ALPHA-2026-04-12.txt"
    assert path.read_text(encoding="utf-8") == (
        "station ALPHA — 2026-04-12\n"
        "  readings 24\n"
        "  minimum  12.0\n"
        "  maximum  22.0\n"
        "  mean     17.0\n"
    )


def test_summarise_is_pure_and_needs_no_patching_at_all():
    # The one part of report_v1 that was already testable, because it takes its
    # input as an argument instead of fetching it.
    assert report_v1.summarise(READINGS) == {
        "count": 24,
        "minimum": 12.0,
        "maximum": 22.0,
        "mean": 17.0,
    }
