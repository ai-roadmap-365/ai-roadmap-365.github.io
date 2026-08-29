# Dependencies — Day 067 lab

**Python 3 only. No third-party packages.**

- `python3` (3.8 or newer; tested on 3.14.0). You installed this on Day 43.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — in fact only `os` (in `examples/compare.py`, to
  find `accounts.csv` next to the script). The classes themselves import
  nothing at all.

There is deliberately no `requirements.txt` and no virtual environment step.
Classes are part of the Python language, not a package: `class`, `self`,
`@property`, `@staticmethod`, `@classmethod`, `vars()`, and `type()` are all
built in, which is why every framework you meet later can assume them.

Check your Python is present and new enough:

```bash
python3 --version
```

If that prints `Python 3.8` or higher, you are ready. Windows users: run the
commands inside WSL, or use `python` in place of `python3` if that is how
Python is exposed on your system. The code is pure standard-library Python
and behaves identically everywhere.
