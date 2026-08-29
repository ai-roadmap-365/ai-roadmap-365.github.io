# Dependencies — Day 053 lab

**Python 3 only. No third-party packages.**

- `python3` (3.7 or newer; tested on 3.14). The insertion-order guarantee this
  lab relies on is a language feature since 3.7. Preinstalled on most Linux
  distributions and installable on macOS; you set this up on Day 43.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Only the Python standard library is used — specifically the `sys` module,
  which ships with Python. The extension exercises optionally use
  `collections` (also standard library). There is deliberately no
  `requirements.txt`: a dictionary lab should run on a plain Python install
  with nothing to install first.

Check your Python is present and new enough:

```bash
python3 --version
```

If that prints `Python 3.7` or higher, you are ready. Windows users: run the
commands inside WSL, or use `python` in place of `python3` if that is how
Python is exposed on your system.
