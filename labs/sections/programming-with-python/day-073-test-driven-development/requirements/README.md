# Dependencies — Day 073 lab

**One third-party package: pytest. No network at test time, no API key, no
account.**

```text
pytest==9.1.1
```

That is the whole of `requirements.txt`, pinned to an exact version so the
output you see matches the captures in `expected-output/` and
`examples/cycles/` line for line. pytest is free and open source under the MIT
licence — its documentation is listed in the lesson's sources, and
`pytest --version` on this machine printed `pytest 9.1.1` on 2026-07-19.

## The one-time install

You built a virtual environment on Day 43; this is the same three lines.

```bash
cd labs/sections/programming-with-python/day-073-test-driven-development
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
```

The `pip install` step is the only moment this lab touches the network.
Afterwards every command — the kata, the suite, the test runner — runs fully
offline. `.venv/` is ignored by version control; never commit it.

If you would rather not create a lab-local environment, point the runner at a
pytest you already have:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

`tests/run_tests.sh` looks for that override first, then `./.venv/bin/pytest`,
then whatever is on your `PATH`, and stops with instructions if it finds none.

## What else the lab uses

| Module | Used in | Why |
| --- | --- | --- |
| `pytest` | `examples/test_bowling.py`, your `starter/test_bowling.py` | test discovery, plain `assert`, and `pytest.raises` for the three refusals |
| `bash` | `tests/run_tests.sh` | the outer runner, so the command is the same as every other day of this course |
| `sed` | `tests/run_tests.sh` | breaking a throwaway copy of the implementation, to prove the suite can fail |
| standard library only | `examples/bowling.py` | the scorer imports nothing at all |

The implementation under test has **no imports**. That is not an accident: a
pure function over a list of integers is the easiest thing in the world to
drive test-first, which is exactly why this kata was chosen to teach the
technique. Day 74 takes on the harder case, where the code you are testing
talks to something outside itself.

## Windows

Use WSL and follow the Linux path, or substitute `python` for `python3` and
`.venv\Scripts\pytest.exe` for `.venv/bin/pytest`. The test runner is a bash
script, so it needs WSL, Git Bash, or another bash. Nothing about the kata
itself is platform-specific.
