# Security notes — Day 054 lab

- **What the program does:** reads two command-line arguments, splits them on
  commas, computes set algebra, and prints a report. It makes **no network
  connections**, reads and writes **no files**, and changes **no settings**.
  The test runner is equally self-contained and non-interactive.

- **Validate input; never execute it.** This lab turns text into *data* — it
  splits strings and builds sets — and never turns text into *code*. **Never**
  use `eval()` or `exec()` to "parse" what a user typed: those functions run
  the string as Python, so a malicious value could delete files or open a
  network connection. Splitting on commas and building a set, as this program
  does, can only ever produce data.

- **Sets are a real security tool.** Fast, correct membership testing is a
  security primitive: an allow-list or a block-list of terms, IDs, or hosts is
  naturally a `set`, and `value in allowed` is an O(1) check that stays fast at
  scale. Using a set for these checks (instead of scanning a list) is both
  faster and less error-prone.

- **Hashable keys only.** A set and a dict key must be **hashable** — which
  means immutable. This is why the program uses tuples, not lists, for grouped
  values: a tuple can be a set member or a dict key, a list cannot. Reaching
  for the immutable type here is a habit that prevents a whole class of bugs.

- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. As always in this course, if a script ever asks you to run it with
  elevated privileges, stop and read it first.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/collections_tool.py` and `tests/run_tests.sh` before running
  them. Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
