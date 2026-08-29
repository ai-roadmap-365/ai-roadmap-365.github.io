# Dependencies — Day 066 lab

**Python 3 only. No third-party packages, no network, no API key.**

- `python3` (3.8 or newer; tested on 3.14.0). You set this up on Day 43.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only: `json`, `logging`, `sys`, `time`, and `traceback`.
  Every one of those ships with Python. There is deliberately no
  `requirements.txt` — error handling is a language feature and a design
  discipline, not something you install.

Check your Python is present and new enough:

```bash
python3 --version
```

If that prints `Python 3.8` or higher you are ready.

## A note on Python versions

Python 3.11 and newer print *fine-grained* tracebacks: under the failing
line you get `~~~^^^` carets pointing at the exact sub-expression that
raised. On 3.8-3.10 those caret lines are simply absent and everything else
is the same. The lab's captured output was taken on 3.14.0, so it shows the
carets; nothing in the tests depends on them.

Exception chaining (`raise ... from err`, `__cause__`, and the
"The above exception was the direct cause of the following exception" line)
has been in Python since 3.0, so it works on every version this course
supports.

## Windows

Run the commands inside WSL and follow the Linux path. Native Windows Python
raises exactly the same exceptions, but the test runner needs `bash`, and
tracebacks print Windows-style paths.
