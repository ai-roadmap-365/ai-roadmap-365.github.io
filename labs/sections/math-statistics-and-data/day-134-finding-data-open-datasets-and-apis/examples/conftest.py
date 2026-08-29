"""Shared fixtures: two mock API instances with different rate-limit patience.

``mock_api`` relents after 2 requests -- the "source that eventually lets
you through" case. ``stubborn_mock_api`` relents after 10, which is more
than any test's attempt budget -- the "source that never relents within a
sane budget" case. Both are started and stopped inside the fixture, so a
test that never touches them never binds a port, and one that does leaves
nothing running when it finishes.
"""

import pytest

from mock_server import serve_mock_api


@pytest.fixture
def mock_api():
    with serve_mock_api(rate_limit_trigger_count=2) as api:
        yield api


@pytest.fixture
def stubborn_mock_api():
    with serve_mock_api(rate_limit_trigger_count=10) as api:
        yield api
