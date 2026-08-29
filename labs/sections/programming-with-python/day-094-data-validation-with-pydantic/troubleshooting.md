# Troubleshooting — Day 094

Every message quoted here was produced by this lab on the machine it was
written on. If yours differs in wording, check the `type` rather than the
prose: `type` is the part pydantic treats as an interface.

## Setup

### `ModuleNotFoundError: No module named 'pydantic'`

The interpreter running the script is not the one the packages were installed
into. This is the single most common problem in a lab with dependencies.

```bash
cd labs/sections/programming-with-python/day-094-data-validation-with-pydantic
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import pydantic; print(pydantic.VERSION)"   # -> 2.13.4
```

Then run everything with `.venv/bin/python3` and `.venv/bin/pytest`, not with a
bare `python3`.

### `FAIL: pytest not found.` from the test harness

The harness deliberately stops rather than skipping. It resolves its tools in
three steps — an explicit override, then `./.venv/bin/`, then `PATH` — so
either create the virtual environment as above, or point it at one you have:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

### `pip install` fails with a network error

The install is the only step that needs the network. If you are behind a proxy
or offline, nothing else in the lab will help — pydantic's validation core is a
compiled extension (`pydantic-core`), so there is no pure-Python fallback to
fall back to. Get the two wheels onto the machine and install from a local
directory:

```bash
.venv/bin/pip install --no-index --find-links /path/to/wheels -r requirements/requirements.txt
```

### `ModuleNotFoundError: No module named 'pydantic_settings'`

Expected. `pydantic-settings` is a separate distribution and this lab does not
install it. The lesson describes it and reproduces no output from it. Section 1
of `tests/run_tests.sh` asserts it is absent, precisely so that claim cannot
quietly rot.

## Running the examples

### `ModuleNotFoundError: No module named 'models'`

`examples/gate.py` imports its schema by bare name, so it has to be run with
`examples/` on the path. Two things work:

```bash
python3 examples/gate.py          # from the lab directory — works
cd examples && python3 gate.py    # also works
```

What does not work is importing `gate` from somewhere else without putting
`examples/` on `sys.path` first. `tests/test_validation.py` does exactly that,
at the top, and the comment there explains why.

### `FileNotFoundError: ... data/raw-readings.json`

You moved a script out of its directory. `examples/gate.py`,
`examples/scratch_demo.py` and `starter/byhand.py` all locate the batch
relative to their own `__file__`, two levels up. Run them from where they live,
or pass `--input` explicitly:

```bash
python3 examples/gate.py --input data/raw-readings.json
```

## Validation errors you will actually see

### The `loc` names `pm2_5` but my field is called `pm25`

```
pm2_5 [float_parsing]
```

Correct and deliberate. `pm25` carries `Field(alias="pm2_5")` because the
vendor's export writes it that way. **The error names the key the caller
actually sent**, which is what makes the report usable by whoever owns the
source file. If you assert on `("pm25",)` your test will fail; assert on
`("pm2_5",)`.

The same alias flips the other way on the way out: `model_dump()` gives you
`pm25`, and `model_dump(by_alias=True)` gives you `pm2_5`.

### `band [extra_forbidden]` when I feed a dump back in

```python
Reading.model_validate(reading.model_dump())   # refused: band [extra_forbidden]
```

`band` is a `computed_field`. It is serialised because a consumer wants it, and
it is refused on the way back in because `extra="forbid"` is doing its job:
nothing computed is an input. **Both behaviours are correct; the bug is
assuming they compose.** The round trip that works is:

```python
Reading.model_validate(reading.model_dump(by_alias=True, exclude={"band"}))
```

`examples/serialize.py` demonstrates both.

### `value_error` with an empty `loc`

```
<record> [value_error]
```

That is a `model_validator(mode="after")` failing. Its `loc` is empty because
no single field is at fault — the *combination* is. In this lab it is the rule
that a PM2.5 reading above 500 must carry a note explaining it. Record 9 in the
batch is the one that trips it; record 10 has the same magnitude and a note, and
passes.

### `datetime_from_date_parsing` on a date that looks fine to me

```
recorded_at [datetime_from_date_parsing]
```

`15/08/2026 10:00` is unambiguous to a human in most of the world and ambiguous
to a parser everywhere. pydantic parses ISO 8601 and a few other well-defined
formats; day-first and month-first are not distinguishable from the string, so
it refuses rather than guessing. If you must accept a local format, do the
parsing yourself in a `field_validator(mode="before")` and hand pydantic a real
`datetime`.

### A naive timestamp is refused with `value_error`, not a parse error

`2026-08-15T06:00:00` parses perfectly well as a `datetime` — it just has no
timezone. That is caught one step later, by the `field_validator` on
`recorded_at`, which raises `ValueError`. Hence `value_error` rather than a
parsing type. A naive timestamp is an ambiguity, not a time.

### `int_type` when I passed `True`

Only in strict mode, and only where you asked for something other than `bool`.
In lax mode `True` validates as the integer `1`, because `bool` genuinely is a
subclass of `int` in Python. The miniature validator in
`examples/scratch_validator.py` refuses it on purpose, and the comment there
explains the reasoning: letting a checkbox arrive where a count was wanted is a
bug that survives to production.

### `frozen_instance`, not `frozen_field`

Assigning to a field of `Station` raises with `type="frozen_instance"`, because
`frozen=True` is set on the whole model rather than on one field. Observed in
pydantic 2.13.4. This is a good illustration of why the tests assert on `type`
and never on `msg`: even the `type` names have a shape worth checking rather
than assuming.

## The gate

### The gate raised instead of returning

If a `ValidationError` escapes `run_gate`, the `except ValidationError` is
missing or is catching the wrong thing. That is exercise 8, and it is the whole
point of the file. A pipeline that raises on the first malformed row processes
nothing and tells you about one problem.

Note the ordering trap: pull the raw id with `raw.get("reading_id")` **before**
validating, or a record that fails validation cannot be named in the report.

### The duplicate id is not being caught

It cannot be caught by the schema. Uniqueness is a property of the *batch*, not
of the record, so `Reading` has no way to see it. It is caught in `run_gate` by
keeping a dict of ids already seen — exercise 9.

### `out/` keeps reappearing

`examples/gate.py` writes there by default. Either clean up afterwards:

```bash
rm -rf out
```

or send it elsewhere: `python3 examples/gate.py --out-dir /tmp/day094`. The test
harness uses a temporary directory for exactly this reason and checks at the end
that no `out/` was left behind.

## The tests

### `pytest starter` says `1 passed, 9 skipped`

That is the correct starting state. Delete the `@pytest.mark.skip(...)` line
above a test as its exercise starts passing.

### A starter test fails with `ModuleNotFoundError: No module named 'models'`

Run it as `pytest starter` from the lab directory. `starter/pytest.ini` sets
`pythonpath = .` relative to that directory so the starter modules can import
each other by bare name.

### `__pycache__` directories appearing everywhere

Set `PYTHONDONTWRITEBYTECODE=1`, which is what the harness does. To clean up:

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
```

Resolve the path first and keep it inside this lab directory — never run a
recursive delete against an unresolved variable.
