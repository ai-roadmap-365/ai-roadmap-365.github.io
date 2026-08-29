"""Make this directory's own matrix.py the one its tests import.

Both `examples/` and `starter/` contain a module called `matrix`, and pytest
imports test files by putting their directory on `sys.path`. Without this
file, running `pytest` across both directories at once would import whichever
`matrix` was seen first and then reuse it for the other suite — so the starter
tests would silently pass against the reference solution instead of skipping.
That is a wrong answer with a green tick on it, which is the worst kind.

So: put this directory first on the import path, and drop any already-imported
`matrix` or `dataset` that came from somewhere else.
"""

import sys
from pathlib import Path

HERE = str(Path(__file__).parent.resolve())

if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)

for name in ("matrix", "dataset"):
    module = sys.modules.get(name)
    origin = getattr(module, "__file__", "") or ""
    if module is not None and not origin.startswith(HERE):
        del sys.modules[name]
