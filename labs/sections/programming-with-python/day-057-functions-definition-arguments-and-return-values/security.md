# Security notes — Day 057 lab

- **What the code does:** defines a set of pure functions that transform text
  and numbers and return values. It makes **no network connections**, needs
  **no privileges**, writes **no files**, and reads no input except the
  arguments each function is called with. `demo.py` and the test runner only
  import the module and print or assert on return values.

- **Pure functions are safe functions.** Because these functions take input
  only from their arguments and return a value without touching the outside
  world, they cannot leak data, corrupt a file, or surprise a caller with a
  side effect. This is not only good design — it is a security property: the
  smaller a function's contact with the world, the smaller its attack surface
  and the easier it is to reason about.

- **Never build behaviour out of `eval()` or `exec()`.** A tempting shortcut
  for a "calculator" or "formula" function is to pass a user string to
  `eval()`. Do not: `eval` and `exec` execute their argument as Python, so a
  malicious value could delete files or open a network connection. Every
  function here does its work with ordinary operations on its arguments —
  arithmetic, string methods, comprehensions — which can never execute
  arbitrary code.

- **Validate at the boundary; fail loudly.** `mean` and `summarize` raise a
  clear `ValueError` on an empty sequence, and `clamp` raises when `low`
  exceeds `high`, rather than returning a silently wrong number or dividing
  by zero. An exception a caller can catch is safer than a plausible-looking
  wrong answer that flows into the next computation unnoticed.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/library.py`, `examples/demo.py`, and `tests/run_tests.sh`
  before running them. Running unread scripts is one of the most common ways
  developers get compromised; the course's rule is that every lab script is
  small enough to read and understand first.
