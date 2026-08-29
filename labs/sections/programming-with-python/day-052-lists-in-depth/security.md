# Security notes — Day 052 lab

- **What the program does:** builds a few lists in memory, slices, sorts, and
  transforms them, and prints the results. It makes **no network
  connections**, reads and writes **no files**, and changes **no settings**.
  The test runner is equally self-contained and non-interactive.

- **Copy before you mutate — the safety habit of this lab.** The functions
  here take a list and return a *new* list, never changing the caller's data.
  That discipline is a correctness and safety property, not just style: a
  function that quietly mutates a list it was handed can corrupt data another
  part of the program still depends on, and such bugs are silent — nothing
  crashes, the numbers are just wrong. When you need to change a list you were
  given, copy it first (`items[:]`, `list(items)`, or `copy.deepcopy` for
  nested lists) and change the copy.

- **Shallow vs deep copy is a real trap.** A shallow copy (`items[:]`)
  duplicates the outer list but shares the inner lists. If your data is nested
  — a matrix, a batch of records — mutating an inner list still shows through
  both copies. Reach for `copy.deepcopy` when the nested contents must be
  independent. Knowing which copy you have prevents a class of hard-to-find
  data-corruption bugs.

- **Validate input; never execute it.** This lab does not read untrusted
  input, but the rule from Day 49 still stands: to turn text into data, parse
  it with safe converters (`int()`, `float()`), never with `eval()` or
  `exec()`, which run their argument as code.

- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. As always in this course, if a script ever asks you to run it with
  elevated privileges, stop and read it first.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/toolkit.py` and `tests/run_tests.sh` before running them.
  Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
