# Security notes — Day 059 lab

- **What the package does:** reads one text file you name (or standard input),
  splits it into words, counts them, and prints a small report. It makes **no
  network connections**, needs **no privileges**, and writes **no files** — it
  only reads the input you point it at. The test runner reads only the files in
  this lab and leaves nothing behind.

- **Imports run code — know what you import.** An `import` statement does not
  just "load data": Python *executes* the top level of a module the first time
  it is imported. That is why the responsibility modules here keep their top
  level to a compiled regular expression and function definitions, with no work
  or side effects at import time. Never `import` a module you have not read, and
  never add a module to `sys.path` from an untrusted location — anything on the
  path can be imported and run.

- **`sys.path` order is a trust decision.** Python imports the first matching
  module it finds while scanning `sys.path`, and for `python3 -m` the current
  directory comes first. A file named, say, `re.py` sitting in your working
  directory could *shadow* the standard-library `re` module and be imported
  instead. Name your modules so they do not collide with the standard library
  (this package uses `tokens.py`, not `tokenize.py`, for exactly that reason),
  and be deliberate about what directories are on the path.

- **Parse text as data, never as code.** This tool treats its input purely as
  text to be tokenized and counted. Do **not** reach for `eval()` or `exec()`
  to "process" a line of a file — those execute the string as Python, so a
  malicious input could delete files or open a connection. Reading text and
  matching it with `re` cannot execute anything; that is the safe pattern.

- **The `__main__` guard is a safety feature too.** Because the real work is
  behind `if __name__ == "__main__":`, importing the package (for a test, or to
  reuse `report`) never launches the program or reads a file on its own. A
  module that *did* work at import time could surprise anyone who imported it —
  reading files, printing, or worse — so keep runnable behaviour behind the
  guard.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/wordstats/*.py` and `tests/run_tests.sh` before running them.
  Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
