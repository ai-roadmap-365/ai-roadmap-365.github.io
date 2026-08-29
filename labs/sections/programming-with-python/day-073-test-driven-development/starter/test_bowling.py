"""Your bowling suite. One test arrives per cycle — never two.

Read `cycles.md` and work through it in order. For each cycle:

  1. Add exactly ONE test function here, at the bottom, in cycle order.
  2. Run the suite and WATCH IT FAIL. Read the failure. Is it failing for the
     reason you expected, or for a boring reason like a typo in the import?
  3. Paste that failure into the RED slot for the cycle in `cycles.md`.
  4. Write the least code in `bowling.py` that makes it pass.
  5. Run the suite again, confirm every test passes, and paste that run into
     the GREEN slot in `cycles.md`.

Run the suite from the lab directory (the directory that holds `starter/`):

    .venv/bin/pytest starter/test_bowling.py

The import below is deliberately `import bowling` rather than
`from bowling import score`. A missing name then fails inside the one test
that uses it, instead of stopping collection for the whole file — which is
what lets each cycle show up as "1 failed, N passed" rather than one error.
"""

import pytest  # noqa: F401  — you need this from cycle 5 onward

import bowling  # noqa: F401  — your implementation module, empty for now


# Cycle 1 starts here. Delete this comment and write your first test function.
