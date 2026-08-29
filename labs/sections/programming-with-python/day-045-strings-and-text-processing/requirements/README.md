# Dependencies — Day 045 lab

**Only Python 3 and a POSIX shell.** This lab installs nothing:

- `python3` (version 3.8 or newer — any modern install works; captured on
  3.14). Check with `python3 --version`.
- `bash` (for the test runner — preinstalled on macOS and Linux).

The program uses only the Python standard library (`pathlib`), which ships
with Python itself. There is deliberately no `requirements.txt`: string and
text processing are core language features, so no third-party package is
needed.

**Windows:** run the commands inside WSL (Windows Subsystem for Linux) so the
`bash tests/run_tests.sh` step works, or run the Python program directly with
`python examples\text_report.py` in PowerShell and check the numbers against
`expected-output/FIELDS.md` by hand.
