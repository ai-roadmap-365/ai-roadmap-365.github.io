# Dependencies — Day 060 lab

**Python 3 only. No third-party packages — that is the entire point of this lab.**

- `python3` (3.8 or newer; tested on 3.14.0). Preinstalled on most Linux
  distributions and installable on macOS; you set this up on Day 43.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Only the Python standard library is used — specifically `pathlib`,
  `collections`, `datetime`, `json`, `argparse`, and `sys`, all of which ship
  with Python. There is deliberately no `requirements.txt`: this lab exists to
  show that a real, useful directory-audit tool needs nothing installed at
  all.

Check your Python is present and new enough:

```bash
python3 --version
```

If that prints `Python 3.8` or higher, you are ready. Windows users: run the
commands inside WSL, or use `python` in place of `python3` if that is how
Python is exposed on your system. The tool itself is pure standard-library
Python and behaves identically everywhere.
