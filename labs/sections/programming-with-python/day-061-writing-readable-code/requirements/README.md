# Dependencies — Day 061 lab

**Python 3 only. No third-party packages required.**

- `python3` (3.9 or newer; tested on 3.14.0). The reference uses
  `list[float]` type-hint syntax, which reads cleanly on 3.9+. Preinstalled on
  most Linux distributions and installable on macOS; you set this up on Day 43.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Only the Python standard library is used — `sys` and nothing else. There is
  deliberately no `requirements.txt`: refactoring for readability needs no
  libraries at all.

Check your Python is present and new enough:

```bash
python3 --version
```

## Optional style tools (not required)

The lesson introduces a **formatter** (Black) and a **linter** (Ruff, or the
older flake8). They make style automatic, but they are entirely optional here:
the test suite runs with or without them, and simply **skips** their checks
when they are absent. If you want to try them:

```bash
python3 -m pip install black ruff      # optional, one-time
black examples/report.py               # auto-format in place
ruff check examples/report.py          # report style/lint issues
```

If `pip` is restricted on your machine, skip this entirely — everything the
lab asserts works on a plain Python install with nothing downloaded. Windows
users: run the commands inside WSL, or use `python` in place of `python3` if
that is how Python is exposed on your system.
