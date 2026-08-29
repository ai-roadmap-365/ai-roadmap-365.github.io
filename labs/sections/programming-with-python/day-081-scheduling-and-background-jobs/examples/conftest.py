"""Make this directory importable so the tests can `import runner` directly.

Without this, `pytest examples` collects the test files but cannot import the
modules beside them, because the lab has no package layout — deliberately, so
that every file here can also be run with `python3 examples/<name>.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
