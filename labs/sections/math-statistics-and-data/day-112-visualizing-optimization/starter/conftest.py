"""Make this directory's own modules the ones its tests import.

Identical in purpose to examples/conftest.py: both directories define
`dataset`, `gridviz`, `descent` and `imaging`, and without this file pytest
would import whichever it saw first and reuse it for the other suite.
"""

import sys
from pathlib import Path

HERE = str(Path(__file__).parent.resolve())

if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)

for name in ("dataset", "gridviz", "descent", "imaging"):
    module = sys.modules.get(name)
    origin = getattr(module, "__file__", "") or ""
    if module is not None and not origin.startswith(HERE):
        del sys.modules[name]
