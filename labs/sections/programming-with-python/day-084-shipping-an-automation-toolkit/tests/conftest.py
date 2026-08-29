"""Make the reference package importable without installing it.

The lab runs its pytest suite against `examples/src/feedkit` directly, so the
unit tests work before you have installed anything. The separate question — does
the INSTALLED console script work — is checked by `tests/run_tests.sh`, which
does a real `pip install -e` and then runs the command by name.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# FEEDKIT_SRC lets the harness point this suite at a DIFFERENT copy of the
# package — which is how it proves the suite is not vacuous: it breaks one line
# in a temporary copy and demands that these tests go red.
override = os.environ.get("FEEDKIT_SRC")
SRC = Path(override) if override else Path(__file__).resolve().parent.parent / "examples" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
