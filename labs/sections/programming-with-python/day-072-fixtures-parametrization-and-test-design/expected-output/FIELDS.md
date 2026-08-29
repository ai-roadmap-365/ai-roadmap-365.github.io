# Expected output — Day 072 lab

These are real captured runs from the authoring machine (macOS 26.5.1, Apple
Silicon, Python 3.14.0, pytest 9.1.1, bash 3.2.57, 2026-07-19). Nothing in
this lab reads the clock, the network, or a random number, and every file it
writes goes into a temporary directory pytest creates, so the same commands
produce the same numbers on any machine with Python 3 and pytest 9.

Only the elapsed times vary — `in 0.03s` on one machine may be `in 0.09s` on
another. Ignore them. Every other number below is required.

## Files

- `sample-run.txt` — the starter suite, then the refactored suite, then the
  collection listing that proves parametrization expanded, then the `-k` and
  `-m` selections, then the fixture-scope demonstration run with `-s`, then a
  single test showing `yield`-fixture teardown output, and finally the
  built-in `tmp_path`, `capsys` and `monkeypatch` demonstrations.
- `test-run.txt` — a full run of `bash tests/run_tests.sh`: 38 checks, 0
  failures, exit 0.
- `broken-run.txt` — what the refactored suite does when one comparison in
  `practice_store.py` is damaged on purpose. This is the capture worth
  studying: the suite goes red, and it names the exact parametrized case.

## Required numbers

| Command (from the lab directory) | Required result |
| --- | --- |
| `cd starter && pytest -q` | `13 passed` |
| `cd starter && pytest --collect-only -q \| tail -2` | `13 tests collected` |
| `grep -c 'store = PracticeStore(path)' starter/test_practice_store.py` | `8` |
| `cd examples && pytest -q` | `39 passed, 2 xfailed` |
| `cd examples && pytest --collect-only -q \| tail -2` | `41 tests collected` |
| `cd examples && pytest --collect-only -q -k refuses \| tail -2` | `11/41 tests collected (30 deselected)` |
| `cd examples && pytest --collect-only -q -m validation \| tail -2` | `21/41 tests collected (20 deselected)` |
| `cd examples && pytest --collect-only -q -m "not slow" \| tail -2` | `40/41 tests collected (1 deselected)` |
| `cd examples && pytest scopes -s -q` | `4 passed, 1 xfailed` |
| `bash tests/run_tests.sh` | `38 checks, 0 failure(s).` and exit 0 |

Read the second and fifth rows together. The starter has 13 hand-written test
functions and pytest collects 13 items — one to one, because nothing is
parametrized. The refactored suite has **22** hand-written test functions
(4 in `test_sessions.py`, 8 in `test_store.py`, 5 in
`test_builtin_fixtures.py`, 5 in `scopes/`) and pytest collects **41** items,
because four of those functions are parametrized. That
gap is the entire argument for parametrization: more cases without more code,
each one reported by name.

Count it precisely if you want to see where the 41 comes from:
3 + 6 + 9 + 3 = 21 items from `test_sessions.py`, plus 7 + 3 = 10 from
`test_store.py`, plus 5 from `test_builtin_fixtures.py`, plus 5 from
`scopes/`.

## Required fixture-scope behaviour

`cd examples && pytest scopes -s -q` must show exactly these counts across the
whole run of the `scopes/` directory (two modules, five tests):

| Fixture | Scope | Times its body runs | Why |
| --- | --- | --- | --- |
| `session_scoped` | `session` | 1 | One pytest process, one construction |
| `module_scoped` | `module` | 2 | `test_scopes_first.py` and `test_scopes_second.py` |
| `function_scoped` | `function` | 4 | The four tests that request it |

The teardown half of `function_scoped` must also appear **4** times. The
fourth of those four tests fails on purpose (it is marked `xfail`), so a
fourth teardown line is the proof that teardown after `yield` runs whether the
test passed or failed.

## Required test ids

`cd examples && pytest --collect-only -q test_sessions.py` must list ids that
a human chose, not ids pytest invented:

```text
test_sessions.py::test_refuses_a_bad_value[ref-without-prefix]
test_sessions.py::test_refuses_a_bad_value[ref-too-short]
test_sessions.py::test_refuses_a_bad_value[topic-not-lower-case]
test_sessions.py::test_refuses_a_bad_value[topic-padded-with-spaces]
test_sessions.py::test_refuses_a_bad_value[minutes-zero]
test_sessions.py::test_refuses_a_bad_value[minutes-over-the-cap]
```

If you see `[ref0]`, `[ref1]`, `[ref2]` instead, the `ids=` argument is
missing. The suite still works; the failure report just stops telling you
anything useful.

The stacked decorators must produce the nine-item cross product, with the
**bottom** decorator's parameter appearing first in the id:

```text
test_sessions.py::test_every_topic_accepts_every_legal_duration[1-python]
test_sessions.py::test_every_topic_accepts_every_legal_duration[1-linear-algebra]
test_sessions.py::test_every_topic_accepts_every_legal_duration[1-statistics]
test_sessions.py::test_every_topic_accepts_every_legal_duration[45-python]
...
test_sessions.py::test_every_topic_accepts_every_legal_duration[600-statistics]
```

## Required failure behaviour

Change `if self.minutes <= 0:` to `if self.minutes < 0:` in
`examples/practice_store.py` and the suite must go red with exactly one
failure, naming the case:

```text
FAILED test_sessions.py::test_refuses_a_bad_value[minutes-zero] - Failed: DID...
1 failed, 38 passed, 2 xfailed in 0.04s
```

Two things in that line are the day's argument in miniature. First, the suite
noticed — a suite that stays green against broken code is worthless. Second,
`1 failed, 38 passed`: the other five cases of the same function still ran and
still passed. Had those six cases been a `for` loop inside one test, the loop
would have stopped at the first failure and reported one broken test with no
detail about the rest.

## Platform differences

- **macOS and Linux** — identical output. `tmp_path` lands under
  `/private/var/folders/...` on macOS and `/tmp/pytest-of-<user>/...` on most
  Linux systems; nothing in this lab prints those paths, so no capture depends
  on them.
- **Windows** — run the commands in WSL and follow the Linux path. In a native
  Windows shell, `bash tests/run_tests.sh` will not run (it is a bash script),
  but every `pytest` command in the tables above works unchanged in PowerShell
  once you activate the virtual environment with `.venv\Scripts\activate`. The
  counts are the same.
- The elapsed time on every summary line will differ from the captures. That
  is the only field that is allowed to differ.
