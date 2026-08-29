"""Make this directory's own eigen.py the one its tests import.

Both `examples/` and `starter/` contain modules called `eigen` and `dataset`,
and pytest imports test files by putting their directory on `sys.path`.
Without this file, running a bare `pytest` across both directories at once
would import whichever `eigen` was seen first and then reuse it for the other
suite — so these starter tests would silently pass against the reference
solution instead of skipping. That is a wrong answer with a green tick on it,
which is the worst kind.

So: put this directory first on the import path, and drop any already-imported
`eigen` or `dataset` that came from somewhere else.

Section 4 of `tests/run_tests.sh` checks that this still works, by comparing
the skip count from `pytest starter` against the skip count from a bare
`pytest` over the whole lab. If this guard ever stops working, that check goes
red rather than the lab quietly lying to you.
"""

import sys
from pathlib import Path

HERE = str(Path(__file__).parent.resolve())

if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)

for name in ("eigen", "dataset"):
    module = sys.modules.get(name)
    origin = getattr(module, "__file__", "") or ""
    if module is not None and not origin.startswith(HERE):
        del sys.modules[name]
