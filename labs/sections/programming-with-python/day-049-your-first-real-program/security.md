# Security notes — Day 049 lab

- **What the program does:** reads two command-line arguments, converts a
  number, and prints the result. It makes **no network connections**, reads
  and writes **no files**, and changes **no settings**. The test runner is
  equally self-contained and non-interactive.

- **Validate input; never execute it.** The most important security habit in
  this lab is turning text into data safely. The converter uses `float()`,
  which can only ever produce a number or raise an error — it cannot run
  code. **Never** use `eval()` or `exec()` on input, no matter how tempting
  it looks for "evaluating" what a user typed: those functions execute the
  string as Python, so a malicious value could delete files or open a
  network connection. Parse and validate input into safe types at the
  boundary, exactly as `parse_args` does.

- **Fail loudly, not silently.** On bad input the program prints a clear
  message to standard error and exits with a non-zero code. Silent failure —
  computing a wrong answer from bad input and reporting it confidently — is
  worse than a crash, because no one notices. Validating at the boundary
  prevents both.

- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. As always in this course, if a script ever asks you to run it with
  elevated privileges, stop and read it first.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/converter.py` and `tests/run_tests.sh` before running them.
  Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
