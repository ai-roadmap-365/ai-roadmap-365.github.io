# Security notes — Day 063 lab

- **What the tool does:** reads text from a file you name or from standard
  input, computes a numeric summary, and prints it. It makes **no network
  connections**, needs **no privileges**, and writes **no files** — the
  pure core writes nothing at all, and the shell only reads. The test
  runner creates one throwaway input file with `mktemp` and removes it.

- **A pure core cannot do damage.** The design idea of this lab is also a
  security property: because `summary_core.py` performs no I/O — no
  `open()`, no network, no `os`/`subprocess` — its functions physically
  cannot delete a file, spend money, or leak data, no matter what input
  they are handed. All the dangerous capabilities live in the thin shell,
  in one small, readable place you can audit. Keeping side effects at the
  edges is a real security practice, not just a tidiness preference.

- **Validate input at the boundary; never execute it.** Numbers enter
  through `parse_numbers`, which uses `float()` — a safe conversion that
  can only ever produce a number or raise `ValueError`. Do **not** reach
  for `eval()`/`exec()` to "read" a number or an expression from input;
  those execute the string as Python, so a malicious value could run
  arbitrary code. `float()` (and, for whole numbers, `int()`) is the safe
  way to turn text into a number.

- **Fail loudly, not silently.** Every error path — a non-numeric token,
  empty input, a missing file — prints a message to standard error and
  returns exit code 1, so a person or a script notices. Silently printing
  a wrong or empty summary while reporting success is worse than an error.

- **Reading before running:** every file in this lab is short and
  commented. Read `examples/summary_core.py`, `examples/summary.py`, and
  `tests/run_tests.sh` before running them. Running unread scripts is one
  of the most common ways developers get compromised; the course's rule is
  that every lab script is small enough to read and understand first.
