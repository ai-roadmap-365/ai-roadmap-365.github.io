# Security notes — Day 050 lab

- **What the program does:** reads two command-line arguments, decides a
  category, and prints the result. It makes **no network connections**, reads
  and writes **no files**, and changes **no settings**. The test runner is
  equally self-contained and non-interactive.

- **Validate input at the boundary; never execute it.** The most important
  security habit in this lab is turning text into data safely. `parse_args`
  checks the argument count, converts the score with `float()` (which can only
  ever produce a number or raise an error — it cannot run code), normalises and
  checks the status against an explicit allow-list, and rejects out-of-range
  scores with a chained comparison. **Never** use `eval()` or `exec()` on input,
  no matter how convenient it looks: those functions execute the string as
  Python, so a malicious value could delete files or open a network connection.

- **Conditionals are your access control.** A decision written with `or` where
  it needed `and` can admit input it should have refused. Order matters too:
  short-circuit evaluation lets you check "is this present and well-formed?"
  before you act on a value, so a bad input never reaches the code that trusts
  it. Getting the boolean logic right *is* the security work here.

- **Fail loudly, not silently.** On bad input the program prints a clear message
  to standard error and exits with a non-zero code (2). Silently classifying a
  malformed input and reporting a confident wrong answer is worse than a crash,
  because no one notices. Validating at the boundary prevents both.

- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. If a script ever asks you to run it with elevated privileges, stop and
  read it first.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/triage.py` and `tests/run_tests.sh` before running them.
  Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
