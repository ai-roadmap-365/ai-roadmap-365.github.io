"""The naive test. It PASSES, and it is worthless.

Run it on its own to watch it go green:

    pytest examples/test_autospec_naive.py -q

The test author read `latest_average`, saw `client.fetch_radings(...)`, and
stubbed exactly that. A bare `Mock()` never objects, so the typo is reproduced
in the test and confirmed by the test. The suite is green; the first production
request raises `AttributeError`.
"""

from unittest.mock import Mock

from typo_under_test import latest_average


def test_latest_average_with_a_bare_mock():
    client = Mock()
    client.fetch_radings.return_value = [10.0, 20.0, 30.0]

    assert latest_average(client, "ALPHA", "2026-04-12") == 20.0
    client.fetch_radings.assert_called_once_with("ALPHA", "2026-04-12")
