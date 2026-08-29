# Troubleshooting — Day 074 lab

## Install and tooling

**`pytest: command not found`, or `.venv/bin/pytest` does not exist.**
The virtual environment was not created, or was created somewhere else. From
this directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version    # expect: pytest 9.1.1
```

**`FAIL: pytest not found.` from `tests/run_tests.sh`.**
The runner looks in three places, in order: the `PYTEST` environment variable,
`.venv/bin/pytest` in this directory, and your `PATH`. If pytest lives
somewhere else, point the runner at it:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

**`ModuleNotFoundError: No module named 'report_v2'` (or `fakes`, or
`sensor_service`).**
pytest puts the *test file's own directory* on the import path. Run
`pytest examples/...` or `pytest starter/...` — never copy one test file
somewhere else and run it there. If you are using `python3 -c` directly, set
the path yourself: `PYTHONPATH=examples python3 -c "..."`.

**`SyntaxError` on the `with (` line in a patch test.**
The parenthesised multi-line `with` form needs Python 3.10 or newer. Either
upgrade, or rewrite it as nested `with` statements:

```python
with patch("report_v1.fetch_readings", return_value=READINGS) as fetch:
    with patch("report_v1.datetime") as fake_datetime:
        ...
```

## Patching

**The patch appears to do nothing: the test is slow, or the numbers are
random.**
This is the day's headline mistake, and the fix is always the same. You patched
where the function was **defined**; you must patch where the name is **looked
up**.

```python
# report_v1.py contains:  from sensor_service import fetch_readings
patch("sensor_service.fetch_readings")   # reaches nobody
patch("report_v1.fetch_readings")        # this is the one
```

The tell is the clock: a patched call returns instantly, a real one takes about
0.4 s here. If a "unit test" takes longer than a few milliseconds, something
real is still being called.

**`AttributeError: <module 'report_v1' from '...'> does not have the attribute
'fech_readings'`.**
Good news, actually. `patch` checks that the attribute exists before replacing
it, so a typo in the *target string* is caught immediately. Fix the spelling.
Note the asymmetry that the whole lab is about: `patch` checks the target name,
but a bare `Mock()` does **not** check the names you then use on it.

**A test passes on its own and fails when the file runs as a whole.**
A patch escaped its scope. `patch` as a decorator or in a `with` block undoes
itself on exit even if the test raises; `patcher.start()` without a matching
`stop()` does not, and leaks into every test after it. If you must use
`start()`, use `addfinalizer` or a fixture so `stop()` cannot be skipped — or
just use `monkeypatch`, which undoes everything automatically.

**Patching a whole module (`patch("report_v1.datetime")`) feels wrong.**
It is. `report_v1.py` says `import datetime`, so the only name it looks up is
the module itself, and replacing it wholesale is the only way in. That
awkwardness is a message about the design of `report_v1`, not about
`unittest.mock` — and it disappears entirely in `report_v2`, where the clock is
a parameter.

## Mocks and doubles

**A test is green and the feature is broken.**
Start by asking what the double was built from. A bare `Mock()` answers yes to
every question: `client.fetch_radings` exists, and
`client.fetch_readings("A", "B", retries=3, nonsense=True)` is fine. Rebuild it
with `create_autospec(SensorClient, instance=True)` and run again. Watch
`examples/autospec_demo.py` do exactly this.

**`AttributeError: Mock object has no attribute 'fetch_radings'`.**
The specced double is doing its job. Either the name is misspelled in the code
under test — fix the code, that is the bug this catches — or the real class
genuinely gained a method and your spec source is out of date.

**`TypeError: got an unexpected keyword argument 'retries'` from an autospec'd
double.**
Only `create_autospec` and `autospec=True` check signatures; `spec=` does not.
The call in your code does not match the real method. Again: fix the call.

**`AttributeError: 'assert_called_once_wiht' is not a valid assertion.`**
Python guards the specific case of a misspelled `assert_` method, so this one
raises rather than silently passing. It is the only typo a bare `Mock()`
catches — every other misspelled attribute is invented on demand.

**`StopIteration` from a mock with `side_effect` set to a list.**
The list ran out: the code under test called it more times than you scripted.
Either the retry count is higher than you thought, or the call is inside a loop
you forgot about. Count the calls with `mock.call_count` and script that many.

## The refactored core

**`NotImplementedError: Exercise ...`.**
Expected until you finish that exercise. Delete the `raise` line and write the
body described in the docstring above it.

**`starter/report_v2.py imports nothing that does I/O` fails.**
You added an import the core is not allowed to have — commonly `time` (for the
backoff) or `pathlib` (for the file). Neither belongs here: the backoff sleeps
through the injected `sleep` parameter, and the file is written by an adapter
that receives the finished report. The check parses the file with `ast`, so a
comment mentioning `pathlib` is not a violation; an actual import is.

**`your core builds a report from an empty directory` fails.**
Something in your core needs the world. Run the same code yourself to see the
real error:

```bash
cd "$(mktemp -d)" && PYTHONPATH=/full/path/to/lab/starter python3 -c "
import datetime
from report_v2 import build_report
from fakes import StubSensorClient, frozen_clock
print(build_report('ALPHA', clock=frozen_clock(datetime.date(2026,4,12)),
                   client=StubSensorClient([12.0, 14.0, 20.0, 22.0]*6)).render())
"
```

**The mean is `16.8` or `17` instead of `17.0`.**
Use `round(total / count, 1)`, and format with `:.1f` in `render`. The readings
`[12.0, 14.0, 20.0, 22.0] * 6` average to exactly 17.0 — check it by hand.

**The retry test says `waits == [0.5]` when you expected `[0.5, 1.0]`.**
You slept after the final attempt, or not between the second and third. The
rule is: sleep only when another attempt is left, and pass
`backoff_seconds * attempt`, where `attempt` counts from 1.

**The dummy raised `AssertionError` in the `attempts=0` test.**
Your `build_report` called the client before validating `attempts`. Move the
guard to the first line of the function. This is precisely what a dummy is for.

## Things that are not problems

- **`examples/test_autospec_specced.py` fails.** It is supposed to. So is
  `examples/test_patch_wrong_target.py`. The test suite asserts both failures.
- **`examples/test_autospec_naive.py` passes.** Also supposed to, and it is the
  most useful failure in the lab — a green test proving nothing.
- **`demo.py` prints different readings each run.** Section 1 calls the real
  stand-in service deliberately. Sections 2 to 6 are identical every time.
- **Mock reprs show different `id=` numbers each run.** Object addresses.
  Ignore them; never assert on them.
