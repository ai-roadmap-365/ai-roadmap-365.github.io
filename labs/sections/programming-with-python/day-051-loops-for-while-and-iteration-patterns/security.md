# Security notes — Day 051 lab

- **What the program does:** reads a command name and optional argument from
  `argv`, reads whitespace-separated numbers from standard input, runs one
  iteration pattern, and prints the result. It makes **no network
  connections**, reads and writes **no files**, and changes **no settings**.
  The test runner is equally self-contained and non-interactive.

- **Validate input; never execute it.** The program turns input text into
  numbers with `int()`, which can only ever produce an integer or raise an
  error — it cannot run code. **Never** use `eval()` or `exec()` on input, no
  matter how convenient it seems for "parsing" what a user typed: those
  functions execute the string as Python, so a malicious value could delete
  files or open a network connection. Parse and validate input into safe
  types at the boundary, exactly as `read_numbers` and `int_arg` do.

- **Bound loops fed by external input.** A loop whose length is controlled by
  untrusted input is a denial-of-service lever: an attacker who can make your
  loop run "one more time" a billion times can freeze the program. This lab's
  loops are bounded by the input actually provided, and a real service should
  additionally cap how much input it will accept. The general rule: never
  trust a stopping condition that depends entirely on data you did not
  generate, and give loops over external input a hard upper bound.

- **Fail loudly, not silently.** On bad input the program prints a clear
  message to standard error and exits with a non-zero code. Silent failure —
  computing a wrong answer from bad input and reporting it confidently — is
  worse than a crash, because no one notices. Validating at the boundary
  prevents both.

- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. As always in this course, if a script ever asks you to run it with
  elevated privileges, stop and read it first.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/patterns.py` and `tests/run_tests.sh` before running them.
  Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
