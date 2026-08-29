"""Make this directory's own matmul.py the one its tests import.

Both `examples/` and `starter/` contain a module called `matmul`, and pytest
imports test files by putting their directory on `sys.path`. Without this file,
running `pytest` across both directories at once would import whichever
`matmul` was seen first and then reuse it for the other suite — so the starter
tests would silently pass against the reference solution instead of skipping.
That is a wrong answer with a green tick on it, which is the worst kind.

This is not a hypothetical. It happened while building the Day 100 lab, where
eleven unwritten exercises reported as passing, and it was caught only because
the number of skips changed between two runs that should have agreed. Section 4
of `tests/run_tests.sh` now asserts that the skip count is identical whether the
suites are collected separately or together, so the same mistake cannot come
back quietly.

So: put this directory first on the import path, and drop any already-imported
`matmul`, `dataset` or `answers` that came from somewhere else.
"""

import sys
from pathlib import Path

HERE = str(Path(__file__).parent.resolve())

if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)

for name in ("matmul", "dataset", "answers"):
    module = sys.modules.get(name)
    origin = getattr(module, "__file__", "") or ""
    if module is not None and not origin.startswith(HERE):
        del sys.modules[name]
