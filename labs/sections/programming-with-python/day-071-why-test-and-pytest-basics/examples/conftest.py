"""Shared setup that pytest finds by itself.

You never import this file and nothing in the test suite mentions it by name.
pytest looks for files called `conftest.py` in the directory it is collecting
from and in every parent directory up to the rootdir, imports them before
collection starts, and makes whatever they define available to every test file
underneath them. That is the whole mechanism.

Two things live here:

* `SAMPLE`, an ordinary module-level constant the tests import by name;
* `sample_text`, a *fixture* — a function decorated with `@pytest.fixture`
  whose return value is handed to any test that names `sample_text` as a
  parameter. Fixtures are Day 72's subject. Today you only need to recognise
  one when you see it: a test parameter that is not a value but a request.
"""

import pytest

# Twelve words. Counted by hand, deliberately, because a test whose expected
# value came out of the code it is testing proves nothing at all.
#
#   the quick brown fox jumps over the lazy dog the dog barks
#    1    2     3    4    5    6    7   8    9   10  11   12
#
# Frequencies: the=3, dog=2, and one each of barks, brown, fox, jumps, lazy,
# over, quick. Total characters in words: 46, so the mean is 46/12 = 3.8333...
SAMPLE = "The quick brown fox jumps over the lazy dog. The dog barks."


@pytest.fixture
def sample_text() -> str:
    """The sample sentence, handed fresh to every test that asks for it."""
    return SAMPLE
