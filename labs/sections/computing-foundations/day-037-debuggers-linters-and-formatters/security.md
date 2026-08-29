# Security notes — Day 37 lab

- **What the scripts do:** `quality_check.sh` and `tests/run_tests.sh` only
  *read* and *analyze* local files — they run `bash -n` (a syntax check that
  parses but does not execute the target), `grep`, and `sed`. They make **no
  network connections** and change nothing outside their own console output
  and a temporary directory the tests clean up automatically.
- **The sample is never executed.** `examples/samples/buggy.sh` is an exhibit
  to inspect, not to run. The lab deliberately *analyzes* it statically; it
  never runs it. This models the real rule below.
- **Never run untrusted scripts.** Static analysis (linting, `bash -n`,
  reading the source) is safe on code you do not trust because it does not
  execute that code. *Running* an unread script from the internet is one of
  the most common ways developers get compromised. Read a script, and lint it,
  before you ever run it — and never `sudo` a script you have not read.
- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. The only step that touches the network is the *optional* ShellCheck
  install, which you run deliberately from your OS package manager.
- **Privacy:** the scripts expose only what is already in the files you point
  them at. They collect no system information and send nothing anywhere.
