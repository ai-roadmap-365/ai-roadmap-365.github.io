# Dependencies — Day 058 lab

**Python 3 only. No third-party packages.**

- `python3` (3.8 or newer; tested on 3.14.0). Preinstalled on most Linux
  distributions and installable on macOS; you set this up earlier in the
  course.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Only the Python standard library is used — in fact only core language
  features (`*args`, `**kwargs`, closures, `nonlocal`) and no imports at all
  in the module itself. There is deliberately no `requirements.txt`: these
  are built-in language features that run on any plain Python install.

Check your Python is present and new enough:

```bash
python3 --version
```

If that prints `Python 3.8` or higher, you are ready. Windows users: run the
commands inside WSL, or use `python` in place of `python3` if that is how
Python is exposed on your system. The module is pure standard-library Python
and behaves identically everywhere.
