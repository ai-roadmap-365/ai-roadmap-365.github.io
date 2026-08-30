"""Make this lab importable when the suite runs.

pytest puts the test file's own directory on sys.path, not the lab root, so a
test that does `from examples.<module> import ...` -- or imports a module that
lives in examples/ directly -- fails without this. Putting it here rather than
in run_tests.sh means a bare `pytest` from the lab root works too.
"""

import os
import sys

LAB = os.path.dirname(os.path.abspath(__file__))
for candidate in (LAB, os.path.join(LAB, "examples")):
    if os.path.isdir(candidate) and candidate not in sys.path:
        sys.path.insert(0, candidate)
