"""Make the lab directory importable so tests can `from examples...`.

pytest puts the test file's own directory on sys.path, not the lab root, so
`from examples.the_perceptron_lib import ...` fails without this. Placing the
file here also means a bare `pytest` run from the lab root works, not just
`bash tests/run_tests.sh`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
