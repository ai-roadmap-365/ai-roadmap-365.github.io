# Day 126 lab — A Pipeline You Can Re-run

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Reproducible Cleaning Pipeline
- **Day number:** 126 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-126-a-reproducible-cleaning-pipeline
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-126-a-reproducible-cleaning-pipeline` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises, each proving one real property a reproducible
pandas 3.0.5 cleaning pipeline must have, by running code and reading real
values. The through-line: **a notebook that produced the right answer once
is not a pipeline.** The opening failure this lab is built on: a clip step
that recomputes its threshold from whatever data is CURRENTLY passing
through it looks correct the first time and produces a different, silently
wrong result the second time it runs on its own output — exactly what a
retried scheduled job does by accident, routinely. `pipeline(pipeline(df))`
must equal `pipeline(df)`, exactly, and exercise 1 makes both halves of
that sentence concrete: the failure, then the fix. Every later exercise
adds one more property a real pipeline needs — determinism and an explicit
tie-break, a step log that reconciles, contracts at both ends that can
genuinely fail, `.pipe()` equivalence, declared order-dependence, a
Parquet checkpoint that preserves dtypes exactly, and a manifest that
answers "which data produced this number?" without guessing.

## Learning objectives

By the end of this lab you will be able to:

- Demonstrate that a step which recomputes its threshold from the current
  frame is not idempotent, and fix it by reading the threshold from
  configuration instead.
- Assert `pipeline(pipeline(df))` equals `pipeline(df)` exactly for a
  correctly designed pipeline.
- Show that two independent runs on the same input hash identically, and
  that an explicit tie-break makes a sort's result independent of arrival
  order among tied values.
- Read a step log and confirm it reconciles: every step's rows-out equals
  the next step's rows-in, and the total change equals the sum of the
  per-step deltas.
- Write an input contract that raises, naming the column, on a missing
  column or a wrong dtype.
- Write an output contract that raises, naming the violated condition,
  when a step is sabotaged — proving the contract can genuinely fail.
- Prove a `.pipe()` chain produces a frame identical to sequential function
  application.
- Demonstrate that swapping two steps changes the result, and state which
  order the pipeline declares and why.
- Prove a Parquet checkpoint round-trip preserves every dtype exactly,
  including a nullable `Int64` column's missing value.
- Build a manifest recording an input hash, a config hash, a step log and
  an output hash, and show it is stable across runs and sensitive to a
  one-byte input change.

## Prerequisites

- **Day 120** — Series and DataFrames, dtypes and Copy-on-Write.
- **Day 121** — loading and inspecting data; Parquet preserving dtypes
  where CSV does not, used directly in exercise 8.
- **Day 122** — boolean masks and the partition invariant, the ancestor of
  this lab's step-log reconciliation habit.
- **Day 123** — `groupby`, split-apply-combine, and the reconciliation
  habit this lab's step log generalises to a whole pipeline.
- **Day 124** — merging and reshaping, and pandas 3.0's `str` extension
  dtype for plain string columns, which this lab's input contract and
  idempotence guard are written against directly.
- **Day 125** — the cleaning techniques (imputation, `to_numeric(errors=
  "coerce")`, string normalisation) this lab's steps apply; this lab does
  not re-teach them, only the engineering that makes them reproducible.
- A working `python3` on your `PATH` to create the lab's virtual
  environment.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given the pinned versions below |
| Windows | Use WSL and follow the Linux path. `mktemp -d` is used inside `tests/run_tests.sh`; native Windows was not tested and no output is claimed for it |

## Hardware requirements

Anything. The largest structure built in this lab is a seven-row
DataFrame. No GPU, no network beyond the one-time install, no meaningful
disk use — the only files this lab writes live inside its own `.venv` or
inside a pytest-managed temporary directory that pytest itself removes.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `pandas` | 3.0.5 exactly | 3.0.5 | Every step, `.pipe()` chain, `to_csv`, `to_parquet`/`read_parquet` |
| `pyarrow` | 25.0.1 | 25.0.1 | pandas 3.0's Parquet engine, used by exercise 8's checkpoint |
| `numpy` | 2.5.2 | 2.5.2 | A pandas dependency; not called directly in this lab |
| `pytest` | 9.1.1 | 9.1.1 | The test harness, plus `monkeypatch` and `tmp_path` |
| `bash` | 3.2 | 3.2.57 | The outer test harness |

`hashlib`, `json`, `logging` and `pathlib` are Python standard library —
already present, no install, no cost — and do the hashing, serialisation
and path handling in `pipeline.py`.

Check your Python in one line: `python3 --version`.

## Free and open-source options

Everything here is free.

- **pandas** (BSD 3-Clause), **NumPy** (BSD 3-Clause) and **pytest** (MIT)
  are fully open source with no paid tier.
- **PyArrow** (Apache 2.0) is the Arrow project's Python bindings, also
  fully open source.
- **pandera** (MIT) and **Great Expectations** (Apache 2.0), described
  from their documentation in the lesson's Tools section rather than run
  here, offer declarative alternatives to this lab's hand-written
  contracts, both free with paid hosted tiers for the surrounding
  platform, not the validation library itself.
- **Prefect** and **Dagster**, also described from documentation only,
  offer free open-source cores with paid managed-cloud tiers for
  scheduling and observability at scale.

No account, no key, no paid tier, and no part of this lab is degraded
without one.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-126-a-reproducible-cleaning-pipeline
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import pandas; print(pandas.__version__)"
```

If your tools live somewhere unusual, `tests/run_tests.sh` takes an
override rather than guessing:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## File structure

```text
day-126-a-reproducible-cleaning-pipeline/
├── README.md                     this file
├── metadata.yml                  lab metadata and the recorded run
├── security.md                   what this lab does to your machine
├── troubleshooting.md            grouped by the message you actually see
├── requirements/
│   ├── README.md                  versions, and what each package is for
│   └── requirements.txt           pandas==3.0.5, pyarrow==25.0.1, numpy==2.5.2, pytest==9.1.1
├── starter/                      YOUR work happens here
│   ├── 00_brief.md                exercise-by-exercise instructions
│   ├── data.py                    raw messy orders + CONFIG (read, do not edit)
│   ├── steps.py                   seven pure steps + one deliberately broken step
│   ├── pipeline.py                contracts, step log, hashing, checkpoint, manifest
│   ├── conftest.py                fixtures wrapping data.py
│   └── test_pipeline.py           nine exercises, each a pytest.skip to replace
├── examples/                     the reference. Read AFTER you have tried
│   ├── data.py
│   ├── steps.py
│   ├── pipeline.py
│   ├── conftest.py
│   └── test_pipeline.py           the fully worked, 17-assertion answer key
├── tests/
│   └── run_tests.sh               16 checks of real behaviour
└── expected-output/               captured from a real run on 2026-08-19
    ├── FIELDS.md                   what must match and what may differ
    ├── examples-run.txt            pytest examples -v, captured
    ├── starter-run.txt             pytest starter -v, captured (all skip)
    └── test-run.txt                the full harness run
```

## How to run

```bash
# 1. The reference suite. Read this AFTER you have tried the exercises,
#    never before -- it is the answer key.
.venv/bin/pytest examples
.venv/bin/pytest examples -v

# 2. Where you stand on the exercises. An untouched checkout reports
#    17 skipped, 0 failed.
.venv/bin/pytest starter -v

# 3. Your work: open starter/test_pipeline.py and starter/00_brief.md,
#    and replace each pytest.skip(...) with real assertions.
.venv/bin/pytest starter -v -k test_1
.venv/bin/pytest starter -v -k test_2
# ... and so on through test_9, or just:
.venv/bin/pytest starter -v

# 4. Check everything, including the harness's own proof that it can fail.
bash tests/run_tests.sh
```

**Never run `pytest examples starter` in one command.** Every module in
this lab — `data`, `steps`, `pipeline`, `conftest`, `test_pipeline` — is
defined identically in both directories; pytest imports modules by their
dotted name, and the second directory's collection aborts outright with an
`import file mismatch` rather than quietly shadowing the first. Run them
as two separate commands, always, as shown above.

## What the commands do

**`.venv/bin/pytest examples`** runs the fully worked reference suite: 17
tests across the nine exercises, each asserting a real property of the
pipeline defined in `examples/pipeline.py` and `examples/steps.py`.

**`.venv/bin/pytest starter`** runs your own suite against the identical
pipeline modules, copied into `starter/`. On an untouched checkout, every
one of the 17 tests calls `pytest.skip(...)` and is reported as `s`, so the
run exits 0 with nothing yet proven. Replace a skip with real assertions
and delete the skip line; when all 17 are written and passing, the
exercise is done.

**`bash tests/run_tests.sh`** confirms the installed pandas matches
`requirements.txt` exactly, runs `pytest examples` and requires 17 passed,
runs `pytest starter` and requires 17 skipped on the checked-in state,
confirms `pytest examples starter` in one invocation fails to collect at
all (rather than quietly shadowing), then solves every exercise in a
**scratch copy** made with `mktemp -d` (never touching the real
`starter/test_pipeline.py`), confirms that copy passes in full,
deliberately breaks one assertion inside it, confirms the run now exits
non-zero with a failure reported, restores the line, and confirms it
passes again — proving the suite can genuinely fail rather than merely
claiming to. It finishes by checking no file in `examples/` or `starter/`
contains a URL, that no `.parquet`, `.json` or `.csv` artifact is left
anywhere in the lab, and that nothing else is left on disk.

## Expected output

The harness ends with a real captured line:

```text
16 checks, 0 failure(s)
```

and exits 0. `pytest examples` ends with:

```text
17 passed in 0.08s
```

`pytest starter`, on the checked-in state, ends with:

```text
17 skipped in 0.02s
```

The reconciliation this whole lab is built on, exactly as captured:

```text
raw_orders                          = 7 rows
dedupe_orders step                  = -1 (order_id 3, a resubmission, is caught)
pipeline output                     = 6 rows
sum of every step's delta           = -1  (matches the total change exactly)
```

The full capture of both suites is in `expected-output/`, and
`expected-output/FIELDS.md` says which values are specific to pandas
3.0.5, which are specific to this machine, and which would not differ on
any correctly installed copy of this exact version.

## Validation steps

1. `bash tests/run_tests.sh` ends with `16 checks, 0 failure(s)` and exits
   0.
2. The deliberately broken clip step is NOT idempotent: order 7's amount
   is **approximately 1236.5** after one call and **approximately
   1223.675** after a second call on the same output. The real pipeline
   IS idempotent: `apply_steps_logged(apply_steps_logged(df, config)[0],
   config)[0]` equals `apply_steps_logged(df, config)[0]` exactly.
3. Two independent runs of the real pipeline on fresh `build_raw_orders()`
   calls produce byte-identical content hashes.
4. The step log reconciles: every step's `rows_out` equals the next
   step's `rows_in`, and the total change (**-1**) equals the sum of the
   per-step deltas.
5. The input contract raises `ContractError` naming the missing or
   wrong-dtype column; the output contract raises `ContractError`
   mentioning the clip ceiling when the clip step is sabotaged into a
   no-op, and raises nothing on the real, unmodified pipeline.
6. `run_pipeline_via_pipe` and `run_pipeline` produce identical frames.
7. The declared order (normalise, then dedupe) catches the resubmitted
   order (**6 rows**, order_id 3 gone); the reversed order misses it
   (**7 rows**, both order_id 1 and 3 present).
8. A Parquet checkpoint preserves every dtype exactly, including
   `priority`'s `Int64` dtype and its missing value at order_id 4.
9. The manifest's `input_hash`, `config_hash` and `output_hash` are
   identical across two independent runs on the same input, and changing
   one character in `raw_orders["amount"]` changes both `input_hash` and
   `output_hash` while leaving `config_hash` unchanged.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

16 checks, exit 0 when they all pass and non-zero otherwise. They are
value checks, not file-existence checks: the reference suite's 17
assertions are exercised through `pytest`, the exercise suite is confirmed
all-skip on the checked-in state, and a scratch copy proves the suite can
genuinely fail and then recover.

Override, if your tools are somewhere unusual:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

`tests/run_tests.sh` clears `__pycache__` and `.pytest_cache` both before
and after it runs, and every Parquet checkpoint this lab writes lives in
pytest's own `tmp_path` — cleaned up by pytest itself, never inside this
lab's own directory — so if you only ran the harness, there is nothing
left to clean up.

To remove the lab's virtual environment entirely: `rm -rf .venv`.

To reset your own work and start the exercises again:

```bash
git checkout -- starter/
```

## Troubleshooting

`troubleshooting.md` has the full list, grouped by the message you
actually see. The ones you are most likely to meet:

- **`pytest examples starter` fails with `import file mismatch`** — do
  not run both directories in one invocation; every module in this lab is
  defined identically in both.
- **`ContractError: ... dtype 'float64', expected 'str'`** — you fed a
  pipeline's own output into `run_pipeline` (which checks the INPUT
  contract) instead of `apply_steps_logged` (which does not); idempotence
  is checked with the latter.
- **Exercise 1's broken step "looks" idempotent to you** — confirm you ran
  the earlier steps (parse, normalise, dedupe, impute) before calling the
  broken clip step, in that order.

## Security notes

`security.md` has the full account. In short: this lab opens the network
exactly once, to install its four pinned packages, and everything else
runs offline, writes only inside its own `.venv` or pytest's own temporary
directory, needs no credential, and touches no real data — every row is a
small invented literal.

## Extension exercises

1. **Add a tenth step that genuinely needs the reconciliation habit.**
   Write a step that removes rows where `amount` is negative, add it to
   the declared order, and extend the step log assertions to prove it
   removed exactly the rows you expect.
2. **Replace one hand-written contract with `pandera`.** Read pandera's
   documentation (it is not installed here) and write down, in your own
   words, what `pandera.DataFrameSchema` would need to express to replace
   `check_input_contract` — you do not need to install or run it.
3. **Measure `.pipe()`'s inspectability cost directly.** Rewrite
   `run_pipeline_via_pipe` so you can print `df.shape` after the third
   step without breaking the chain into two statements, and write down
   what you had to change to do it.
4. **Add a config parameter that changes the pipeline's behaviour without
   touching `steps.py` or `pipeline.py`.** For example, add a
   `dedupe_subset` variant that also ignores `priority`, run the pipeline
   with both configs, and compare the row counts and the two configs'
   hashes.
5. **Simulate the scheduled-retry failure directly.** Write a short
   script that calls `run_pipeline` on the same raw data three times in a
   row, feeding each output back in as the next call's input via
   `apply_steps_logged`, and confirm all three outputs are identical —
   then swap in the broken clip step and watch the three outputs diverge.

## Navigation

- **Previous day:** Day 125 — Cleaning Messy Data
  (`labs/sections/math-statistics-and-data/day-125-cleaning-messy-data/`).
- **Next day:** Week 19 begins
  (`labs/sections/math-statistics-and-data/`).
- **Week 18 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-18/`), "Messy
  Dataset Rescue" — building directly on this lab's contracts, step log
  and manifest habits, applied to a dataset of the learner's own.
