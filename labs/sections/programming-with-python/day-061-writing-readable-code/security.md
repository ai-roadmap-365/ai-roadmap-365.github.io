# Security notes — Day 061 lab

- **What the tool does:** reads numbers from the command line, computes summary
  statistics, and prints them. It makes **no network connections**, needs **no
  privileges**, writes **no files**, and touches nothing on disk. The test
  runner only reads the two scripts and runs them; it creates no temporary
  files.

- **Refactoring must not change behaviour — including security behaviour.** The
  discipline this lab teaches (small safe steps, tests after each) is exactly
  how you avoid *accidentally* introducing a bug while "just cleaning up." A
  refactor that quietly changes what the code does is a classic source of
  regressions, some of them security-relevant. The test suite exists so that a
  behaviour change shows up immediately as a red test.

- **Parse input; do not execute it.** Scores enter as strings and are converted
  with `float()`, which can only ever produce a number or raise a `ValueError`.
  Never reach for `eval()` to "read a number" — `eval()` executes its argument
  as Python, so a hostile value could run arbitrary code. `float()` is the safe
  parser, and it is what both versions of the tool use.

- **Readable code is safer code.** A reviewer can only catch a security problem
  they can *see*. Meaningful names, small functions, docstrings, and type hints
  are not just tidiness — they are what make a bug or an unsafe call visible in
  review. Sloppy code hides mistakes from humans and from tools; the whole
  point of this lesson is to stop doing that.

- **Optional tools are optional.** If you choose to install Black or Ruff, get
  them from the official Python Package Index with `python3 -m pip install`,
  and read what any tool does before running it. The lab never requires them
  and never fails when they are missing.

- **Reading before running:** every file in this lab is short and commented.
  Read `starter/messy.py`, `examples/report.py`, and `tests/run_tests.sh`
  before running them. Running unread scripts is one of the most common ways
  developers get compromised; the course's rule is that every lab script is
  small enough to read and understand first.
