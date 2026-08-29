"""Make this directory importable, and put examples/ on the path too.

Your starter modules are imported by name (`import joblock`), and a few of the
exercises lean on finished pieces from `examples/` so you can work on one idea
at a time. `starter` comes first on the path, so your version always wins.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parent / "examples"
for directory in (EXAMPLES, HERE):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
