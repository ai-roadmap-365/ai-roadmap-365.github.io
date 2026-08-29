# Troubleshooting — Day 072 lab

Everything below has been reproduced on the authoring machine. Each entry
gives the message you will actually see, the cause, and the fix.

---

## `FAIL: pytest not found.`

The harness looked in three places and found nothing: the `PYTEST` environment
variable, `.venv/bin/pytest` inside this lab, and your `PATH`.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
bash tests/run_tests.sh
```

If you already have a pytest somewhere else, point the harness at it instead
of installing a second copy:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

---

## `fixture 'empty_store' not found`

pytest looked for a fixture with that name and did not find one in scope. The
message lists every fixture it *did* find, which is the fastest way to see
what went wrong. Three usual causes:

1. **The `conftest.py` is in the wrong directory.** It must sit beside the
   test file, or in a parent directory of it. `conftest.py` is never imported
   by name — pytest finds it by walking up from the test file.
2. **The name is misspelled.** The parameter name *is* the lookup key. There
   is no other link between the test and the fixture.
3. **The fixture is defined in a subdirectory.** A `conftest.py` inside
   `scopes/` is invisible to files above it. That is deliberate, and the test
   harness checks it: a fixture defined in `examples/scopes/conftest.py`
   cannot be requested from `examples/test_store.py`.

To see everything available to a given file:

```bash
pytest --fixtures test_store.py
```

---

## `'slwo' not found in 'markers' configuration option`

You used a marker that is not registered, and `addopts = --strict-markers` in
`pytest.ini` turned that from a warning into an error. This is a feature: an
unregistered marker is almost always a typo, and without strict mode
`@pytest.mark.slwo` silently marks nothing, so `-m slow` quietly skips a test
you thought you were running.

Fix the spelling, or register the marker:

```ini
[pytest]
markers =
    slow: a test that reads the CSV file back off disk
```

---

## `pytest --collect-only -q` says 9 when you expected 13

Your `@pytest.mark.parametrize` did not expand. Check, in order:

- Is the decorator spelled `parametrize`? Not `parameterize`. The British and
  American spellings differ and pytest uses the shorter one.
- Do the names in the first argument match the function's parameters exactly?
  `("ref", "topic", "minutes")` needs a function taking `ref, topic, minutes`.
- Is the second argument a list of *tuples* when there is more than one
  parameter? A flat list of values with a three-name first argument raises a
  collection error rather than expanding.

---

## `In test_x: function uses no argument 'topic'`

You listed a parameter name in `parametrize` that the test function does not
accept. pytest refuses to run rather than silently ignoring it. Add the
parameter to the function signature, or remove it from the decorator.

---

## The `[audit]` print never appears

`pytest` captures standard output and only shows it for failing tests. That is
usually what you want. To see it for passing tests too:

```bash
pytest -s -q
```

`-s` is shorthand for `--capture=no`. Use it while you are exploring, not in
a committed configuration — captured output is what keeps a passing run quiet.

---

## Test ids look like `[ref0]`, `[ref1]`, `[ref2]`

You did not pass `ids=`. pytest generates ids from the values when it can and
falls back to `<name><index>` when it cannot — which happens for tuples,
objects, and anything without a short readable representation. The suite still
runs; the failure report just stops being useful. Add an `ids=` list with one
readable string per case, in the same order.

---

## `PytestUnknownMarkWarning` but the run still passes

Same cause as the strict-markers error above, without `--strict-markers`
switched on. Add `addopts = --strict-markers` to `pytest.ini` so the warning
becomes a failure. A warning in a hundred-line output is a warning nobody
reads.

---

## `ModuleNotFoundError: No module named 'practice_store'`

You ran pytest from the wrong directory. Both suites keep the module under
test beside the tests, and pytest puts a test file's own directory on the
import path. Run from `examples/` or from `starter/`, not from the lab root:

```bash
cd examples && pytest -q
```

---

## A test passes alone and fails as part of the suite

This is the classic symptom of shared mutable state, and it is worth stopping
to understand rather than working around. Some fixture with a scope wider than
`function` is being mutated by one test and observed by another, so the result
depends on the order tests happen to run in.

Find it by narrowing:

```bash
pytest -q path/to/test_file.py::test_that_fails      # passes alone?
pytest -q -k "test_suspect or test_that_fails"       # fails together?
```

The fix is almost never "make the tests run in a fixed order". It is to move
the mutable thing back to `function` scope, or to make it immutable. In this
lab, `sample_sessions` is session-scoped *only* because frozen dataclasses
cannot be mutated; every store fixture is function-scoped for exactly this
reason.

---

## `E fixture 'tmp_path' not found` after you renamed something

`tmp_path` is a built-in, so this message means pytest itself is not the one
running your test — usually because you executed the file directly with
`python3 test_store.py` instead of through pytest. Fixtures only exist inside
a pytest run.

---

## The suite passes but you do not believe it

Good instinct. Prove it can fail, the way Day 71 taught:

```bash
cp -R examples /tmp/day072-check
sed -i.bak 's|if self.minutes <= 0:|if self.minutes < 0:|' /tmp/day072-check/practice_store.py
cd /tmp/day072-check && pytest -q | tail -3
```

You should see `1 failed, 33 passed, 2 xfailed` and the case named as
`test_refuses_a_bad_value[minutes-zero]`. If the suite still passes, the tests
are not testing what you think they are. (On macOS, `sed -i.bak` leaves a
`.bak` file behind; delete the directory afterwards with
`rm -rf /tmp/day072-check`.)

---

## Anything else

Run the harness and read the labelled checks — each one names the property it
was testing, so a `FAIL:` line tells you which of the day's ideas has come
loose:

```bash
bash tests/run_tests.sh
```
