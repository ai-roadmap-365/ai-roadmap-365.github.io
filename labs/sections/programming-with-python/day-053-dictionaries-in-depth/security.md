# Security notes — Day 053 lab

- **What the program does:** reads one command-line argument (text to count,
  or the `--records` flag), builds dictionaries in memory, and prints the
  result. It makes **no network connections**, reads and writes **no files**,
  and changes **no settings**. The test runner is equally self-contained and
  non-interactive.

- **Validate input at the boundary.** The program checks that an argument was
  supplied and that the text contains at least one word, printing a clear error
  to standard error and exiting non-zero otherwise — never a raw `KeyError` or
  traceback. When you build dictionaries from untrusted input (a parsed JSON
  request, say), do the same: never assume an incoming payload has the keys you
  expect. Use `d.get(key, default)` or check `key in d` first, exactly as this
  lab teaches.

- **Never `eval()` input to "parse" it.** As on Day 49, the rule is absolute:
  turn text into data with safe operations (`str.split()`, `int()`, `float()`),
  never by executing it. `eval()` and `exec()` run their argument as Python
  code and must never touch input.

- **Hash randomisation is a feature — leave it on.** Python randomises string
  hashing on each run by default to resist "hash-flooding" attacks, where an
  attacker sends keys engineered to collide into one bucket and slow your
  dictionary from O(1) toward O(n). You get this protection for free; do not
  disable it (`PYTHONHASHSEED`) and do not rely on the exact numeric value of
  `hash()` staying the same across runs.

- **Fail loudly, not silently.** On bad input the program prints a clear
  message to standard error and exits with a non-zero code. Silently computing
  a wrong answer from bad input is worse than a crash, because no one notices.

- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. Read `examples/wordstats.py` and `tests/run_tests.sh` before running
  them — every file in this lab is short enough to read first.
