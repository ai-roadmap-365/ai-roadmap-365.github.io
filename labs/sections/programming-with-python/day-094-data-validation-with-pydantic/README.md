# Day 094 lab — Guard the Boundary

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Data Validation with pydantic
- **Day number:** 94 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-094-data-validation-with-pydantic
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-094-data-validation-with-pydantic` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 94 of 365. A program's boundary is where data stops being your problem and
starts being your responsibility. This lab is that boundary, built twice.

You are handed `data/raw-readings.json`: twelve air-quality records from a
sensor feed, eight of which are wrong in eight different, entirely realistic
ways — a missing required field, a number arriving as a string, a number that
is genuinely not a number, an out-of-range percentage, a misspelled key, a
nested object with its own error, a reused id, and a date in the wrong format.
Your job is to let the good ones through and stop the rest **without ending the
run**.

You build it in three passes:

1. **By hand** (`starter/byhand.py`). One `if` per field per rule, error
   messages written out longhand as prose. It works. It also checks four fields
   out of eight, has no ranges, no patterns, no date handling, no nesting past
   one level and no cross-field rules — and the errors it produces are strings a
   machine cannot act on.
2. **From scratch, properly** (`examples/scratch_validator.py`). A miniature
   validator driven by `__annotations__`: it finds the fields, decides what
   "present" means with a sentinel rather than `None`, applies an explicit
   coercion policy, recurses into nested models, and — the part that looks easy
   and is not — **collects every error instead of raising on the first**. About
   two hundred lines. It rejects 3 of the 12 records.
3. **With pydantic** (`examples/models.py`). The same shape in a fraction of
   the code, plus everything the toy has no vocabulary for. It rejects 7. The
   gate in `examples/gate.py` then rejects an eighth, for a duplicate id — a
   property of the *batch*, which no per-record schema can see.

The gate is the point of the day. `examples/gate.py` processes all twelve
records, emits the four survivors as `accepted.jsonl`, and writes
`rejects.json` naming every refusal with its `loc`, `type`, `msg` and the
`input` that caused it. A `--fail-over` threshold lets it fail the build when
too much of the batch is bad. One malformed row must not stop the run; it must
be counted, named, and reported to whoever owns the source.

Every assertion in this lab is on an error's `type` or `loc`. **Not one reads
`msg`.** `type` and `loc` are the machine-readable contract; `msg` is prose the
library may reword in any release. This is the same argument Day 082 made about
a FastAPI 422 body, and it is literally the same body.

## Learning objectives

- Declare a schema with `BaseModel`, `Field` and `Annotated` constrained types,
  and explain what happens at `model_validate` time.
- State exactly which conversions pydantic performs in lax (default) mode and
  which it refuses, and show the difference with `strict=True`.
- Distinguish **required**, **optional** and **nullable** — three different
  facts that are routinely confused — and prove the distinction from
  `model_json_schema()["required"]`.
- Read a `ValidationError`: find every problem at once, and use `loc` and
  `type` rather than `msg`.
- Express a rule no single field can carry, using `model_validator(mode="after")`.
- Serialize with `model_dump` and `model_dump_json`, and say where the round
  trip is not symmetric and why.
- Build a data-quality gate that survives bad input, counts what it refused,
  and reports it well enough to fix the source.

## Prerequisites

- Day 075 (type hints and static checking) — the annotations you already write
  are what pydantic reads.
- Day 082 (a first web API) — the 422 body you learned to read is a
  `ValidationError` rendered as JSON.
- Day 088 (database constraints) — the third layer that guards the same data.
- Comfort with `dict`, `list`, JSON, and running a script from a terminal.

## Supported operating systems

- macOS 13 or newer (Intel or Apple Silicon)
- Linux (any current distribution with Python 3.10+)
- Windows 10/11 via WSL2, or natively with PowerShell substituting the
  `.venv/bin/...` paths with `.venv\Scripts\...`

Verified on macOS 26.5.2 (Apple Silicon, arm64) with bash 3.2.57.

## Hardware requirements

Nothing unusual. Any machine that runs Python runs this. The whole reference
suite completes in well under a second; the batch is twelve records.

## Required software

| Tool | Version used here | Why |
| --- | --- | --- |
| Python | 3.14.0 | `X \| None` syntax, `Annotated`, modern `typing` |
| pydantic | 2.13.4 | the subject of the day |
| pydantic-core | 2.46.4 | arrives with pydantic; the Rust validation core |
| pytest | 9.1.1 | the reference suite |
| bash | 3.2.57 | `tests/run_tests.sh` |

`pydantic-settings` is a **separate distribution** and is deliberately not
installed here. The lesson describes what it does and reproduces no output from
it; section 1 of the test harness asserts that it really is absent, so that
claim cannot quietly become false.

## Free and open-source options

Everything in this lab is free and open source. pydantic is MIT-licensed;
Python is under the PSF licence; pytest is MIT. There is no paid tier, no
account, no API key and no service to sign up for.

The alternatives the lesson compares — `attrs`, `marshmallow`, `cerberus`,
`jsonschema`, `dataclasses` and `TypedDict` with a static checker — are all
free and open source too. Only pydantic is installed in this lab, and the
lesson says which of them were actually run.

## Installation

Network is needed **once**, here, to fetch two packages. Nothing afterwards
touches the network.

```bash
cd labs/sections/programming-with-python/day-094-data-validation-with-pydantic
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import pydantic; print(pydantic.VERSION)"
```

That last line should print `2.13.4`.

If you would rather not create a virtual environment inside the lab, point the
test harness at an interpreter you already have:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness resolves its tools in that order — explicit override, then
`./.venv/bin/`, then `PATH` — and **fails loudly with install instructions**
rather than skipping when it cannot find them.

## File structure

```
day-094-data-validation-with-pydantic/
├── data/
│   └── raw-readings.json          12 records, 8 of them wrong on purpose
├── examples/                      the reference implementation
│   ├── models.py                  the pydantic schema: Station and Reading
│   ├── gate.py                    the data-quality gate and its report
│   ├── coercion.py                lax vs strict, one table, all measured
│   ├── serialize.py               model_dump, aliases, the broken round trip
│   ├── scratch_validator.py       the miniature validator, standard library only
│   ├── scratch_models.py          the same models for the miniature validator
│   └── scratch_demo.py            the two side by side over the same batch
├── starter/                       your work goes here
│   ├── byhand.py                  the "before": validation written longhand
│   ├── models.py                  exercises 1-6: build the schema
│   ├── gate.py                    exercises 7-10: build the gate
│   ├── test_starter.py            1 passing test, 9 waiting for you
│   └── pytest.ini
├── tests/
│   ├── test_validation.py         47 reference assertions
│   ├── run_tests.sh               the harness: 62 checks
│   └── pytest.ini
├── expected-output/               captured from real runs; see FIELDS.md
├── requirements/requirements.txt
├── troubleshooting.md
├── security.md
├── metadata.yml
└── README.md
```

## How to run

From the lab directory, in this order:

```bash
# 1. The "before" — validation written by hand.
.venv/bin/python3 starter/byhand.py

# 2. Which conversions pydantic performs, and which it refuses.
.venv/bin/python3 examples/coercion.py

# 3. The miniature validator and pydantic over the same twelve records.
.venv/bin/python3 examples/scratch_demo.py

# 4. Serialization, aliases, and where the round trip breaks.
.venv/bin/python3 examples/serialize.py

# 5. The gate. Writes out/accepted.jsonl and out/rejects.json.
.venv/bin/python3 examples/gate.py

# 6. Fail the build when too much of the batch is bad.
.venv/bin/python3 examples/gate.py --fail-over 0.1 ; echo "exit=$?"

# 7. The reference suite, then your own.
.venv/bin/pytest tests
.venv/bin/pytest starter
```

Then work the exercises in `starter/models.py` and `starter/gate.py`, deleting
one `@pytest.mark.skip` line in `starter/test_starter.py` as each one starts to
pass.

## What the commands do

| Command | What it does |
| --- | --- |
| `starter/byhand.py` | Runs hand-written validation over the batch. Accepts 10, rejects 2, and prints what it never even looked at. |
| `examples/coercion.py` | Asks `TypeAdapter` twenty questions, once in lax mode and once with `strict=True`, and prints the answers as a table. Every cell is a real call. |
| `examples/scratch_demo.py` | Runs the miniature validator and the pydantic schema over the same batch and lists exactly which records the toy waved through and why. |
| `examples/serialize.py` | Demonstrates `model_dump` vs `model_dump_json`, `by_alias`, `exclude`, `TypeAdapter`, the generated JSON Schema, and the asymmetric round trip. |
| `examples/gate.py` | The gate. Validates all twelve records, writes `out/accepted.jsonl` and `out/rejects.json`, and prints a per-rejection summary. |
| `examples/gate.py --fail-over F` | The same, but exits 1 when more than fraction `F` of records were rejected. A gate that can never fail the build is a log line. |
| `pytest tests` | The 47 reference assertions. |
| `pytest starter` | Your work. 1 passing, 9 skipped until you unskip them. |
| `bash tests/run_tests.sh` | Everything, plus the checks that the suites are not vacuous. |

## Expected output

`examples/gate.py`:

```
read      12 records from raw-readings.json
accepted  4
rejected  8

  record 2 (RD-0003): operator [missing]
  record 3 (RD-0004): pm2_5 [float_parsing]
  record 4 (RD-0005): humidity_pct [less_than_equal]
  record 5 (RD-0006): humidity_pct [missing]; humidty_pct [extra_forbidden]
  record 6 (RD-0007): station.code [string_pattern_mismatch]
  record 7 (RD-0001): reading_id [duplicate_id]
  record 8 (RD-0009): recorded_at [datetime_from_date_parsing]
  record 9 (RD-0010): <record> [value_error]

wrote accepted.jsonl and rejects.json to out/
```

`examples/scratch_demo.py`, the part that makes the day's argument:

```
from scratch : accepted 9, rejected 3
pydantic     : accepted 5, rejected 7
```

`bash tests/run_tests.sh` ends with:

```
62 checks, 0 failure(s).
```

Full captures of every script live in `expected-output/`. Read
`expected-output/FIELDS.md` first: it says which lines are fixed and which may
legitimately differ on your machine.

## Validation steps

1. `.venv/bin/python3 -c "import pydantic; print(pydantic.VERSION)"` prints
   `2.13.4`.
2. `.venv/bin/pytest tests -q` ends `47 passed`.
3. `.venv/bin/pytest starter -q` ends `1 passed, 9 skipped` before you start,
   and `10 passed` when every exercise is done.
4. `.venv/bin/python3 examples/gate.py` exits 0 on a batch that is two-thirds
   bad, and `out/rejects.json` names all eight refusals.
5. `.venv/bin/python3 examples/gate.py --fail-over 0.1; echo $?` prints `1`.
6. `bash tests/run_tests.sh` reports `62 checks, 0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Seven sections, 62 checks:

1. The installed versions match the pins, the pydantic v2 API surface the
   lesson teaches really exists, and `pydantic-settings` really is absent.
2. `pytest tests` is green at 47, the named tests exist, and a grep confirms
   **no test asserts on an error message string**.
3. The gate runs the whole batch, its printed summary contains every one of the
   eight planted failures by `loc` and `type`, `accepted.jsonl` has four lines,
   `rejects.json` carries all four keys per error, and `--fail-over` really
   fails.
4. Each demo script exits 0 and prints the specific lines the lesson quotes,
   including six rows of the coercion table.
5. The starter runs before you touch it and says honestly what is unfinished.
6. **The starter suite is not vacuous.** The reference implementation is
   dropped in as the answer, every skip is stripped, and all 10 tests must go
   green. Then one rule is broken on purpose — the percentage constraint is
   widened from 0-100 to 0-1000 — and the suite must go **red**, naming the
   range test.
7. Nothing was left behind: no `out/`, no `__pycache__`, no stray virtual
   environment, and no lab source opens a socket at run time.

The harness has been verified to fail when it should: changing `extra="forbid"`
to `extra="ignore"` in `examples/models.py` produces `62 checks, 6 failure(s).`
and exit 1.

## Cleanup

```bash
rm -rf out
rm -rf .pytest_cache tests/.pytest_cache starter/.pytest_cache
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: reset your work
```

The lab writes only inside its own directory (`out/`) and the tests write only
into temporary directories they remove themselves. Nothing is installed
system-wide.

## Troubleshooting

See [troubleshooting.md](./troubleshooting.md) for the errors this lab actually
produces and what each one means — including the two that trip almost everyone:
a `ValidationError` whose `loc` uses the *alias* rather than the field name, and
a round trip that fails because `model_dump()` includes a computed field the
model refuses as input.

## Security notes

See [security.md](./security.md). The short version: validation is a security
control, not a tidiness measure, and the two things this lab is careful about
are (1) never trusting input because it came from a file you own, and (2) never
putting a rejected record's contents somewhere a rejected record's contents
should not go.

## Extension exercises

1. **Make the gate streaming.** Rewrite `run_gate` to take an iterator and
   yield results, so a ten-million-row file does not have to fit in memory.
   Keep the counts exact.
2. **Add a discriminated union.** The feed also carries `type: "calibration"`
   records with a different shape. Model both with `Field(discriminator="type")`
   and confirm the error `loc` names the correct branch.
3. **Quarantine instead of discard.** Write rejected records to
   `out/quarantine.jsonl` alongside the report, then write a second script that
   reads the quarantine, applies one repair rule, and re-validates.
4. **Assert the schema is stable.** Snapshot `Reading.model_json_schema()` to a
   file and add a test that fails when it changes. A schema change is an API
   change; make it visible in review.
5. **Compare a peer.** Express `Station` in `attrs` or `marshmallow`, install
   it in the lab's own virtual environment, and write down the three things
   that were harder and the one that was easier.
6. **Break the report on purpose.** Change `_tidy` to keep only `msg`, then try
   to write a test against it. The difficulty you hit is the lesson.

## Navigation

- Previous lab: `labs/sections/programming-with-python/day-093-orms-and-sqlalchemy/`
- Next lab: `labs/sections/programming-with-python/day-095-dates-times-and-time-zones/`
- Section index: `labs/sections/programming-with-python/`
