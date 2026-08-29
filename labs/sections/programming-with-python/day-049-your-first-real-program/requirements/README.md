# Dependencies — Day 049 lab

**Python 3 only. No third-party packages.**

- `python3` (3.8 or newer; tested on 3.14). Preinstalled on most Linux
  distributions and installable on macOS; you set this up on Day 43.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Only the Python standard library is used — specifically the `sys` module,
  which ships with Python. There is deliberately no `requirements.txt`: a
  first real program should run on a plain Python install with nothing to
  install first.

Check your Python is present and new enough:

```bash
python3 --version
```

If that prints `Python 3.8` or higher, you are ready. Windows users: run the
commands inside WSL, or use `python` in place of `python3` if that is how
Python is exposed on your system.
