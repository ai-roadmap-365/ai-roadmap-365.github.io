# Day 138 lab — Bias You Can Measure

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Data Ethics, Bias, and Provenance
- **Day number:** 138 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-138-data-ethics-bias-and-provenance
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-138-data-ethics-bias-and-provenance` when the site is running.
<!-- generated-links:end -->

## Purpose

Ethics labs usually fail in one of two ways: they hand you principles you
cannot act on, or they preach. This one does neither. Every one of the nine
exercises is either **something you compute** or **something you write down
and check**, and where a question is genuinely a value judgement rather
than a calculation — exercise 5 — the lab says so explicitly and asks you
to assert the disagreement rather than a winner.

The centrepiece is exercise 1, and it is the strongest argument in the day
because it is arithmetic rather than opinion: a sampling frame that reaches
one group at a tenth of its population share produces a model whose error
for that group **does not shrink as the sample grows**. Ten times more data
tightens the confidence interval by about `sqrt(10)` around an answer that
stays exactly as wrong as it was.

Everything after that measures a different way the same thing happens:
coverage mismatch against a reference distribution, a proxy that
under-records one group, one pooled model that is wrong for every subgroup,
three fairness criteria that cannot all hold at once, uniqueness counts on
quasi-identifiers, k-anonymity and its limit, a datasheet contract, and two
dataset versions whose summary statistics are identical while a quarter of
the sample changed.

**Every dataset here is synthetic, deliberately.** A lab about who is
missing from a dataset and about what a table discloses should not be
taught on records describing real people. There is a second reason, and it
is the one that makes the lab possible at all: a constructed population's
true composition is known exactly, so "under-represented by a factor of
ten" is a fact you can assert instead of an impression you can argue about.

## Learning objectives

By the end of this lab you will be able to:

- Show that sampling **bias** is flat in n while sampling **error** falls
  as `1/sqrt(n)`, and report both at three sample sizes rather than
  asserting the distinction from memory.
- Compute a coverage mismatch against a reference population, and name the
  under-represented group with a representation ratio rather than a
  single distance number.
- Demonstrate that optimising a proxy which under-records one group makes
  the true outcome worse for that group while the aggregate barely moves.
- Show that one pooled model can be worse for **every** subgroup than
  per-subgroup models on the same rows, with the wrong slope sign for both.
- Compute demographic parity, equal opportunity and precision for three
  decision policies on one population, and demonstrate that no policy
  satisfies all three when base rates differ.
- Count how many rows of a name-free table are unique on three
  quasi-identifiers, and measure what coarsening one field buys.
- Achieve k-anonymity, report what it cost in suppressed rows, and
  demonstrate a case where k-anonymity holds and a sensitive attribute is
  disclosed anyway.
- Check a dataset's documentation against a provenance contract that names
  each missing field rather than reporting a count.
- Detect a version change that every summary statistic hides, and show that
  only the provenance record makes it visible.

## Prerequisites

- **Day 117** — sampling and the central limit theorem. Exercise 1 is that
  day's bias-versus-error distinction made consequential, and the lab
  assumes you already know that standard error falls as `1/sqrt(n)`.
- **Day 116** — Simpson's paradox and summary statistics as lossy
  compression. Exercise 4 is Simpson's paradox with a cost attached.
- **Day 134** — source assessment, licences and provenance records.
  Exercises 8 and 9 build the datasheet that day's provenance gate was
  pointing at.
- Comfort with pandas `groupby`, NumPy arrays, and pytest.

## Supported operating systems

Written, run and captured on **macOS 26.5.2** (Apple Silicon, arm64).
Runs unchanged on **Linux**. On **Windows**, the Python half runs as-is;
`tests/run_tests.sh` needs Git Bash or WSL and the venv paths differ
(`.venv\Scripts\python.exe`). No Windows run is reproduced here and no
claim is made about one — see `troubleshooting.md`.

## Hardware requirements

Nothing special. The whole harness runs in a couple of seconds and the
largest object it builds is a 50,000-row frame, fitted 40 times. Any
machine that can run Python 3.14 has enough memory.

## Required software

- Python 3.14.0 (3.11 or newer should work; 3.14.0 is what was measured)
- NumPy 2.5.2, pandas 3.0.5, pytest 9.1.1 — pinned in
  `requirements/requirements.txt`
- bash, for `tests/run_tests.sh`

## Free and open-source options

Every dependency of this lab is free and open source: Python (PSF
licence), NumPy and pandas (BSD-3-Clause), pytest (MIT). There is nothing
to buy and no account to create.

The two fairness toolkits the lesson discusses — **Fairlearn** (MIT) and
**AIF360** (Apache-2.0) — are also free and open source, and neither is
installed here. Exercise 5 computes the same three criteria in about
twenty lines of pandas on purpose, so you can see that the incompatibility
between them is arithmetic rather than a library's opinion. **No output
from either toolkit is reproduced anywhere in this lab.**

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-138-data-ethics-bias-and-provenance
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, pandas, pytest; print(numpy.__version__, pandas.__version__, pytest.__version__)"
```

That last line should print `2.5.2 3.0.5 9.1.1`. It is the only step that
touches the network.

## File structure

```
day-138-data-ethics-bias-and-provenance/
├── README.md                  this file
├── metadata.yml               lab metadata and the literal result of the real run
├── security.md                what the lab does to your machine, and why every table is synthetic
├── troubleshooting.md         the failure modes, including the two that are deliberate
├── requirements/
│   ├── README.md              why each pin is here, and what is deliberately absent
│   └── requirements.txt       numpy==2.5.2, pandas==3.0.5, pytest==9.1.1
├── starter/
│   ├── 00_brief.md            the nine exercises explained in full — read this first
│   ├── ethics.py              every measurement function (given to you, complete)
│   ├── fixtures.py            survey counts, reference population, the two datasheets
│   ├── conftest.py            four session fixtures
│   └── test_ethics.py         YOUR nine exercises — each currently a pytest.skip
├── examples/
│   ├── ethics.py              identical to starter/ethics.py
│   ├── fixtures.py            identical to starter/fixtures.py
│   ├── conftest.py            identical to starter/conftest.py
│   └── test_ethics.py         the answer key — all nine solved
├── tests/
│   └── run_tests.sh           the harness: 51 checks, exits 0 only if all pass
└── expected-output/
    ├── FIELDS.md              which captured values are exact and which are not
    ├── test-run.txt           captured harness output
    ├── examples-run.txt       captured `pytest examples -q`
    └── starter-run.txt        captured `pytest starter -v` on an untouched checkout
```

## How to run

```bash
cd labs/sections/math-statistics-and-data/day-138-data-ethics-bias-and-provenance

# 1. read the brief
cat starter/00_brief.md

# 2. see the exercises, all skipped
.venv/bin/pytest starter -v

# 3. solve them one at a time in starter/test_ethics.py
.venv/bin/pytest starter -v

# 4. run the full harness
bash tests/run_tests.sh
echo "exit=$?"
```

**Run `pytest examples` and `pytest starter` as two separate commands.**
Both directories define a module named `test_ethics.py`, and pytest
collects by dotted module name, so `pytest examples starter` in one
invocation aborts with an `import file mismatch`. The harness asserts that
this happens, so the trap is proven rather than merely mentioned.

Check the exit status **directly**, never through a pipe. `bash
tests/run_tests.sh | tail -3` followed by `echo $?` reports `tail`'s status,
not the harness's, and will report success on a failing run.

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates the lab-local environment so these pins cannot collide with anything else on your machine |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs NumPy 2.5.2, pandas 3.0.5, pytest 9.1.1. The only network access in the lab |
| `.venv/bin/pytest starter -v` | Runs your nine exercises. Each skip message names exactly what to assert |
| `.venv/bin/pytest examples -q` | Runs the answer key. Should report `9 passed` before you touch anything |
| `bash tests/run_tests.sh` | The full harness: version check, all nine measurements driven directly, both suites, the collision proof, the can-it-fail proof, and the cleanup check |

## Expected output

On an untouched checkout, `pytest starter -v` reports **`9 skipped`**.
Once every exercise is solved it reports **`9 passed`**, which is what
`pytest examples -q` already reports.

`bash tests/run_tests.sh` ends with:

```
-------------------------------------------------------------
51 checks, 0 failure(s)
```

and exits `0`. The full captured run is in `expected-output/test-run.txt`.
The numbers you should see, from the real run on 2026-08-20:

| Exercise | Measured |
| --- | --- |
| 1 — bias vs n | bias `5.9459` → `5.9384` → `5.9397` (flat); sd `0.06025` → `0.01796` → `0.00524` (falls 11.5× overall) |
| 2 — coverage | total variation distance `0.089583`; west at `0.104167` of its population share |
| 3 — proxy gap | correlation `0.9253`; group B selected at `0.0400` by proxy vs `0.2500` by target; B's need served falls to `0.1785` while the total only falls to `0.9831` |
| 4 — aggregation | pooled slope `+1.9785`, true slopes `-0.9870` and `-0.9991`; pooled RMSE `5.03`/`5.05` vs `1.02`/`1.00` |
| 5 — fairness | base rates `0.66`/`0.34`; parity gaps `0.5000`/`0.0000`/`0.1160`, opportunity gaps `0.3146`/`0.1105`/`0.0000`, precision gaps `0.1210`/`0.3333`/`0.3012` |
| 6 — uniqueness | `2723` of `5000` rows unique on three quasi-identifiers; `13` after coarsening one field |
| 7 — k-anonymity | k=5 achieved by suppressing `794` rows; a 4-anonymous table still discloses `diabetes` |
| 8 — datasheet | 8 fields named as missing, out of 11 required |
| 9 — drift | summary statistics identical; composition shifted `0.2500` |

`expected-output/FIELDS.md` says which of those are exact everywhere and
which are pinned to NumPy 2.5.2 and `seed=138`.

## Validation steps

1. `bash tests/run_tests.sh` ends with `51 checks, 0 failure(s)`.
2. `echo $?` immediately afterwards prints `0` — run it directly, not
   after a pipe.
3. `.venv/bin/pytest examples -q` reports `9 passed`.
4. `.venv/bin/pytest starter -q` reports `9 passed` once you have solved
   every exercise, `9 skipped` before you start.
5. Section 6 of the harness proves the suite can genuinely fail: it copies
   the solved suite to a scratch directory, confirms green, rewrites
   exercise 6's exact uniqueness count from `2_723` to `9_999`, confirms a
   non-zero exit and a printed failure, restores the file and confirms
   green again.
6. Section 7 confirms nothing in the lab code opens a socket and that no
   `__pycache__`, `.pytest_cache` or temporary directory survives the run.

## Tests

`tests/run_tests.sh` runs **51 checks** in seven sections:

1. installed versions match `requirements/requirements.txt` exactly, and
   the harness stops if they do not
2. all nine measurements driven directly against the synthetic
   populations, each printed as a `key=value` line and then asserted by
   name — including the bias-versus-n ladder and all nine fairness gaps
3. `examples/` passes in full (`9 passed`)
4. `starter/` is all-skip on an untouched checkout (`9 skipped`)
5. `pytest examples starter` in one invocation aborts with an
   `import file mismatch`, asserted rather than assumed
6. the prove-it-can-fail cycle described above
7. offline, seeded and clean: no network call in the lab code, every draw
   through `numpy.random.default_rng`, nothing left behind

Every check asserts a **shape or a value**. Nothing asserts a duration.

## Cleanup

```bash
cd labs/sections/math-statistics-and-data/day-138-data-ethics-bias-and-provenance
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: reset your work
```

The harness already removes `__pycache__` and `.pytest_cache` before and
after every run, and its scratch directory is removed by an `EXIT` trap
even if the run is interrupted. The two lines above are only needed if you
ran pytest yourself outside the harness.

## Troubleshooting

See `troubleshooting.md` for the full list. The three most common:

- **`import file mismatch`** — you ran `pytest examples starter` in one
  command. Run them as two commands; the collision is deliberate and
  asserted.
- **`version mismatch: numpy pinned 2.5.2`** — install the pins. Every
  numeric assertion in exercises 1, 3, 4, 6 and 7 is tied to a specific
  NumPy random stream.
- **"exercise 5 must have a right answer"** — it does not, and that is the
  exercise. Each policy closes its own gap exactly and opens another.
  Which criterion your system should satisfy is a value judgement to be
  declared, not a technical default to be accepted.

## Security notes

See `security.md`. In short: one network call ever (the `pip install`), no
sockets, no `sudo`, no credentials, and every table synthetic — because a
lab about who is missing from a dataset and about what a table discloses
should not be taught on records describing real people.

The security file also covers what exercises 6 and 7 are and are not: a
risk-measurement technique, not an attack tool, and one whose *outputs*
are sensitive in their own right when you point it at real data.

## Extension exercises

1. **Push the ladder further.** Add `n = 500_000` to
   `bias_variance_ladder`. Predict the standard deviation before you run
   it (`0.00524 / sqrt(10)`), then check. Confirm the bias has still not
   moved.
2. **Fix the frame, not the sample size.** Add a reweighting step that
   scales each group's contribution by `population_share / frame_share`,
   refit, and measure the group B bias again. Then measure its variance,
   and note what reweighting cost you. This is the honest answer to
   exercise 1 and it is not free.
3. **Find the third fairness policy.** Try to construct a policy that
   closes two gaps exactly. You can. Try to close all three, and watch
   where the arithmetic stops you.
4. **Vary the base rates.** Set both groups' base rates equal in
   `FAIRNESS_CELLS` and re-run exercise 5. All three criteria become
   satisfiable at once. That is the cleanest statement of what actually
   drives the impossibility.
5. **Add a fourth quasi-identifier** to `synthetic_register` — an
   occupation code, say — and re-measure uniqueness. Note how fast it
   climbs, and how much generalisation you now need.
6. **Implement l-diversity** as a function alongside `k_anonymity_level`,
   and then find a table where l-diversity holds and disclosure still
   happens because the sensitive values, while distinct, are all
   semantically close. Every privacy definition has a next limit.
7. **Write a datasheet for a dataset you actually use.** Fill all eleven
   fields honestly. The fields you cannot fill in are the finding.

## Navigation

- Exercise brief: `starter/00_brief.md`
- Answer key: `examples/test_ethics.py` — read it after you have tried
- Captured output: `expected-output/`
- Instructor solution and grading rubric:
