# Day 137 lab — Features That Do Not Cheat

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Thinking in Features
- **Day number:** 137 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-137-thinking-in-features
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-137-thinking-in-features` when the site is running.
<!-- generated-links:end -->

## Purpose

You measure leakage instead of being warned about it.

Nine numbered exercises, each one a before-and-after pair of scores. A
feature derived from the outcome takes a model to 1.00 and removing it
drops the same model to 0.64. A group-mean imputer fitted before the
split is worth eight accuracy points that will not exist in production.
A target encoding computed over the whole table beats an out-of-fold one
by seven. A random split scores 0.88 on time-ordered data where a
time-ordered split scores 0.07 — below the majority-class baseline,
because the model is not uninformed about the new period, it is
confidently wrong about it.

The lesson is not "leakage is bad". It is that **a result which looks too
good is a bug report**, and the first response to an unexpectedly
excellent score is to go looking for the leak.

scikit-learn is not installed here and is not needed. Every model in the
lab is written out in NumPy: a logistic regression trained by gradient
descent (Day 111) and a nearest-centroid classifier built on Day 107's
distance. You have not met a model API yet, and the whole point of this
day is that the feature table decides the score long before the model
does.

## Learning objectives

By the end of this lab you will be able to:

- Plant a target leak, measure what it buys, remove it, and report both
  numbers rather than only the flattering one.
- Separate `fit` from `transform` for every statistic you compute, and
  say from the call site alone whether a test row influenced it.
- Measure the optimism bought by contaminating a scaler and by
  contaminating a group-mean imputer, and explain why one of them is
  worth nothing and the other is worth eight points.
- Build a target encoding three ways — over everything, over training
  rows, and out-of-fold — and measure the gap between them.
- Show that a random split can conceal a temporal leak completely, and
  that the time-ordered number is the trustworthy one.
- Encode a wrapping quantity as sine and cosine and prove, with exact
  distances, that hour 23 and hour 0 are neighbours again.
- Demonstrate that an ordinal code on unordered categories forces
  predictions to move monotonically with an arbitrary number, and that
  one-hot does not.
- Build an interaction that separates classes neither of its components
  separates, and report all three separations.
- Fit a bag-of-words vocabulary on training documents only, handle words
  the training set never contained, and measure what fitting it on
  everything would have bought.
- Write a reusable leakage audit, prove it catches planted leaks and
  flags no honest column, and state plainly which leaks it cannot see.

## Prerequisites

- Day 107 (norms, distances, standardisation), Day 111 (gradient
  descent), Day 116 (descriptive statistics), Day 117 (sampling, and
  bias that does not shrink with n).
- Day 125 (cleaning, imputation, and the fit/transform boundary) and
  Day 126 (pipelines and contracts).
- Days 120-124 for pandas: frames, selection, grouping, merging.
- Comfort reading a small NumPy program. You do not need to have seen a
  machine-learning library; this lab deliberately uses none.

## Supported operating systems

- macOS 13 or newer, Intel or Apple Silicon. Written and run on macOS
  26.5.2 (arm64).
- Any current Linux distribution with Python 3.11 or newer.
- Windows via WSL2, which gives you the bash the harness needs. Native
  PowerShell will run `pytest examples` and `pytest starter` but not
  `tests/run_tests.sh`; that script is bash and is not translated here.

## Hardware requirements

Nothing special. The largest table in the lab is 600 rows by 3 columns,
and the whole suite runs in about 16 seconds on a laptop. Under 300 MB
of disk once the virtual environment is installed, and well under 200 MB
of memory at peak.

## Required software

- Python 3.11 or newer (3.14.0 here).
- `pandas`, `numpy`, `pytest` — pinned in
  `requirements/requirements.txt` to the exact versions used.
- `bash` for the harness (3.2 or newer; 3.2.57 here).

No database, no server, no display, no API key, no account.

## Free and open-source options

Every tool this lab needs is free and open source: Python (PSF licence),
NumPy and pandas (BSD-3-Clause), pytest (MIT). There is no paid tier of
any of them and nothing here is gated.

The lesson also discusses scikit-learn's `Pipeline` and
`ColumnTransformer` — free and BSD-licensed, and **not installed here**,
so nothing in this lab reproduces their output — and one commercial
feature-store product, described from its public documentation only.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-137-thinking-in-features
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import pandas, numpy; print(pandas.__version__, numpy.__version__)"
```

That install is the only step that touches the network. Everything after
it runs offline.

## File structure

```
day-137-thinking-in-features/
├── README.md                 this file
├── metadata.yml              how the lab was actually run
├── security.md               what the lab does to your machine
├── troubleshooting.md        the failures you are most likely to hit
├── requirements/
│   ├── README.md             why the pins are exact
│   └── requirements.txt      pandas, numpy, pytest
├── starter/                  your work goes here
│   ├── 00_brief.md           the exercise brief
│   ├── data.py               seven seeded generators
│   ├── features.py           every encoder, split into fit and transform
│   ├── models.py             logistic regression and nearest centroid
│   ├── experiments.py        the nine measurements
│   ├── conftest.py           one session-scoped fixture per experiment
│   └── test_features.py      nine exercises, each a pytest.skip to replace
├── examples/                 the reference answers — read after you try
│   └── (the same modules, with test_features.py fully written)
├── tests/
│   └── run_tests.sh          the harness: 55 checks
└── expected-output/
    ├── FIELDS.md             what is exact and what may differ
    ├── test-run.txt          the full harness output
    ├── examples-run.txt      pytest examples -q
    └── starter-run.txt       pytest starter -q, untouched
```

## How to run

```bash
cd labs/sections/math-statistics-and-data/day-137-thinking-in-features

.venv/bin/pytest starter -v          # your exercises: 9 skipped to begin with
.venv/bin/pytest examples -q         # the reference answers: 9 passed
bash tests/run_tests.sh              # everything, end to end: 55 checks
```

Run `pytest starter` and `pytest examples` as **two separate commands**.
Both directories hold a module named `test_features.py`, and pytest
collects by dotted module name, so a combined `pytest examples starter`
aborts collection with `import file mismatch`. Section 5 of the harness
runs that combination on purpose to prove it fails rather than silently
letting one directory shadow the other.

## What the commands do

| Command | What it does |
| --- | --- |
| `pytest starter -v` | Runs your nine exercises. On an untouched checkout every one is a `pytest.skip`, so you get 9 skipped and exit 0. |
| `pytest examples -q` | Runs the reference answers. 9 passed. |
| `bash tests/run_tests.sh` | Prints the versions, runs all nine experiments and prints every number, checks 55 claims about them, runs both suites, proves the combined invocation fails, proves the suite can genuinely fail by breaking an assertion in a scratch copy, and confirms nothing was left behind. |

The harness finds `.venv/bin/pytest` first and falls back to whatever is
on your PATH. To point it somewhere else:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## Expected output

The last two lines of `bash tests/run_tests.sh`:

```
-------------------------------------------------------------
55 checks, 0 failure(s)
```

The measurement block from section 2, as captured on the authoring
machine — the whole thing is in `expected-output/test-run.txt`:

```
leak_with=1.0000
leak_without=0.6400
leak_gap_points=36.0000
scaler_optimism_points=-0.0600
imputer_optimism_points=8.2233
te_naive_all=0.6215
te_out_of_fold=0.5535
time_random=0.8833
time_ordered=0.0667
time_majority_baseline=0.9333
cyc_raw_23_0=23.0000
cyc_circle_23_0=0.2611
audit_flagged=days_to_first_invoice,email_template
audit_leak_correlation=0.8468
```

Read `scaler_optimism_points=-0.0600` carefully. It is negative, it is
meant to be, and `expected-output/FIELDS.md` explains why at length.

## Validation steps

1. `bash tests/run_tests.sh` ends with `55 checks, 0 failure(s)` and
   exits 0. Check the exit status directly — never through a pipe:

   ```bash
   bash tests/run_tests.sh; echo "exit=$?"
   ```

2. `.venv/bin/pytest examples -q` ends with `9 passed`.
3. `.venv/bin/pytest starter -q` on an untouched checkout ends with
   `9 skipped`.
4. Prove the suite can fail: change one assertion in
   `examples/test_features.py` to something false, re-run the harness,
   watch it report failures and exit non-zero, then change it back. The
   harness already does exactly this to a scratch copy in section 6.
5. Compare your numbers with `expected-output/FIELDS.md`. Every gap
   should match to the last printed decimal; if one does not, check
   your NumPy and pandas versions against the pins first.

## Tests

`tests/run_tests.sh` runs 55 checks in seven sections:

1. Versions, and that they match the pins exactly. It also asserts that
   scikit-learn is absent, because the lab's text says so.
2. The nine experiments, run for real, every number printed and 30
   claims checked against them — plus the extra binning demonstration
   and two determinism checks.
3. `examples/` passes in full: 9 passed.
4. `starter/` is all-skip on an untouched checkout: 9 skipped.
5. `pytest examples starter` in one invocation aborts, as documented.
6. The suite is proven capable of failing: the solved suite is copied to
   a scratch directory, run green, broken on purpose, confirmed
   non-zero, restored and confirmed green again.
7. Offline and clean: no URL anywhere in the lab code, no networking
   module imported, and no `__pycache__`, `.pytest_cache` or temporary
   directory left behind.

## Cleanup

```bash
cd labs/sections/math-statistics-and-data/day-137-thinking-in-features
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv                # optional: removes the lab virtual environment
git checkout -- starter/    # optional: resets your work
```

The harness removes `__pycache__` and `.pytest_cache` both before and
after its own run, so a clean checkout stays clean. The lab writes no
data file, no image, and no database.

## Troubleshooting

See `troubleshooting.md` for the failures you are most likely to hit:
`pytest: command not found`, `ModuleNotFoundError` from the wrong
directory, `import file mismatch` from the combined invocation, an
assertion that fails on a different NumPy version, and what to do when
one of your own measured gaps comes out with the opposite sign.

## Security notes

See `security.md`. In short: one network connection ever, at install
time; no port bound; no `sudo`; no credential; nothing written outside
this directory; and every row of every table generated from a seeded
`numpy.random.default_rng`, so no real person's data is anywhere near
this lab.

## Extension exercises

1. **Make the audit lie to you.** Construct a leaking feature the audit
   does not flag — for instance one that leaks only within a subgroup —
   and then decide whether you can extend the audit to catch it without
   flagging honest columns. Report what the extension costs in false
   positives.
2. **Group-aware splitting.** The audit cannot see a leak that lives
   across rows: the same customer appearing in both halves of the
   split. Add a `customer_id` to `data.signups()`, make several rows per
   customer, and measure the gap between a plain random split and one
   that keeps each customer entirely on one side.
3. **Smooth the target encoding.** Replace `target_encode_fit` with a
   version that shrinks each category mean towards the global mean in
   proportion to how few rows the category has. Measure whether it beats
   the out-of-fold encoding, and by how much.
4. **A cost column.** Add a `cost_ms` and `available_at_prediction_time`
   annotation to each feature in `experiments.py`, and write a check
   that refuses a feature table containing anything not available at
   prediction time. That check is the one that would have caught
   exercise 1 before the model was ever trained.
5. **Cyclical for other periods.** Day of week wraps at 7, day of year
   at 365 or 366. Encode both, and work out what the leap year does to
   the second one.

## Navigation

- Previous lab: Day 136 — the exploratory data analysis process.
- Next lab: Day 138.
- This lab belongs to Week 20, "Working with Real Data", the last week of
  Course 03. Everything you build here is what the models of Course 04
  will consume.
