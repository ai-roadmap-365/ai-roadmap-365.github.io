# Day 104 lab — Stop Writing the Loop

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** NumPy: Arrays and Vectorized Thinking
- **Day number:** 104 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-104-numpy-arrays-and-vectorized-thinking
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-104-numpy-arrays-and-vectorized-thinking` when the site is running.
<!-- generated-links:end -->

## Purpose

You have spent five days using NumPy as a checking tool beside a from-scratch
implementation. Today it is the subject, and the thing being taught is not a
library — it is a change of habit.

The Python instinct is "loop over the items and do the thing". The NumPy
instinct is "express the whole operation on the whole array and let the library
do the loop in C". This lab moves you from the first to the second by
measurement, and it is equally careful about what the change costs.

Three operations are implemented **twice** — once as an explicit Python loop,
once as a NumPy expression — and the two are compared with `==` over a million
elements, not with a tolerance, because the claim is that they are the *same
computation* rather than a similar one. Then both are timed. On the authoring
machine the vectorised versions ran 106 to 134 times faster; the tests assert
only that the gap is at least twentyfold, which is a claim that survives a
slower laptop.

Around that spine: what an ndarray actually is, with the memory difference
measured rather than asserted — and with the *naive* measurement shown first,
because `sys.getsizeof` on a list says an array is no smaller at all, and
understanding why is more useful than the right number would have been on its
own. Then dtypes and the silent int8 wrap from 127 to -128. Boolean masking,
including the ValueError that `and` raises and `&` does not. `argsort` turning
Day 103's similarity scores into an answer. Views versus copies, which is where
a beginner's hardest bug lives. And `nan`, which is not equal to itself.

The last script is the one the day exists for, and it argues against the rest of
the lab: three situations where the loop is the better code, all three measured.

## Learning objectives

By the end you will be able to:

- Say what an ndarray is in three facts — a fixed dtype, a contiguous block, and
  a shape with strides — and measure the memory consequence honestly.
- Explain why `sys.getsizeof` on a list is not the measurement you want, and
  what the real total is.
- Choose a dtype deliberately, and predict what an int8 does at 127.
- Write a loop and its vectorised equivalent, and show they agree bit for bit.
- Measure both, report the gap with its spread, and say why the figure is not
  worth asserting.
- Build boolean masks, combine them with `&` and `|`, and say why `and` cannot
  work.
- Use `np.where`, mask assignment and fancy indexing in place of `if` in a loop.
- State the axis rule — the axis you name is the one that disappears — and use
  `keepdims` and `np.newaxis` to line shapes up.
- Tell a view from a copy, predict which operations give which, and know what
  `.copy()` is for.
- Use `argsort` for top-k selection, and say why `sort` is the wrong tool.
- Handle missing values: `nan != nan`, `np.isnan`, and the nan-aware
  aggregations.
- Name three situations where vectorising is the wrong choice, with a reason for
  each.

## Prerequisites

- Day 99 — vectors, and the article catalogue this lab ranks.
- Day 100 — matrices; today's arrays are the same objects with more attention
  paid to how they are stored.
- Day 103 — dot products and cosine similarity. The search here is that search,
  vectorised.
- Day 70 — floating point, which is why one section of this lab is about
  precision rather than speed.
- Day 43 — `python3 -m venv` and installing a package with `pip`.
- Days 071–074 — running pytest and reading its output.
- No mathematics beyond school arithmetic.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly rather
  than implying a test that did not happen.

## Hardware requirements

Anything that runs Python. The largest single allocation is a 2000 by 2000
float64 array in the last script, at 32 MB, and it is freed immediately. The
million-element arrays are 8 MB each. Roughly 60 MB of disk for the virtual
environment, almost all of it NumPy.

## Required software

- `python3` — 3.14.0 here.
- `numpy` 2.5.2 and `pytest` 9.1.1, installed into a lab-local virtual
  environment from `requirements/requirements.txt`.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

Both dependencies are free and open source and there is no paid tier of anything
in this lab. NumPy is distributed under the BSD 3-Clause licence and pytest
under the MIT licence. No account, no key, no signup, personally or
commercially.

If you cannot install anything at all, the three loop functions in exercise 1
run on a bare `python3` with `math` alone, and so does the memory measurement —
the 28-bytes-per-integer figure needs only `sys.getsizeof`. What you lose is
every vectorised version, which is most of the lab. `requirements/README.md`
states that cost plainly rather than implying a workaround exists.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-104-numpy-arrays-and-vectorized-thinking
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                              this file
├── metadata.yml                           how the lab was actually run, and when
├── requirements/
│   ├── README.md                          why each package is here, and its licence
│   └── requirements.txt                   numpy==2.5.2, pytest==9.1.1
├── starter/                               your work goes here
│   ├── 00_brief.md                        the seven exercises, in order
│   ├── conftest.py                        makes this directory's vectorize.py the one its tests import
│   ├── dataset.py                         the invented data — read it, do not change it
│   ├── vectorize.py                       exercise 1 — ten functions to write
│   ├── answers.py                         exercises 2 to 7 — forty-two predictions
│   └── test_starter.py                    your running score; unattempted work skips
├── examples/                              the reference, to read after you have tried
│   ├── conftest.py                        the same import guard
│   ├── dataset.py                         the data, seeds and tolerances
│   ├── vectorize.py                       the finished module
│   ├── 01_list_versus_array.py            what an ndarray is, and what it costs
│   ├── 02_dtypes_and_overflow.py          the promise, and breaking it by accident
│   ├── 03_same_answer_faster.py           three operations twice: same answer, 100x apart
│   ├── 04_creating_and_ufuncs.py          eight constructors and the elementwise functions
│   ├── 05_masks_and_selection.py          boolean masking, and why `and` raises
│   ├── 06_axes_views_and_ranking.py       axis, newaxis, views, argsort, top-k
│   ├── 07_nan_and_when_not_to_vectorise.py  missing values, and the case against
│   └── test_reference.py                  107 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                       the bash harness: 80 checks, exits non-zero on any failure
├── expected-output/                       captured from real runs on 2026-08-17
│   ├── FIELDS.md                          what may legitimately differ on your machine
│   ├── 01-list-versus-array.txt
│   ├── 02-dtypes-and-overflow.txt
│   ├── 03-same-answer-faster.txt
│   ├── 04-creating-and-ufuncs.txt
│   ├── 05-masks-and-selection.txt
│   ├── 06-axes-views-and-ranking.txt
│   ├── 07-nan-and-when-not-to-vectorise.txt
│   ├── reference-tests.txt
│   ├── starter-progress.txt
│   └── test-run.txt
├── troubleshooting.md
└── security.md
```

## How to run

Read `starter/00_brief.md` first. Then work, checking yourself as you go:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 70 skipped`. A skip means "not
attempted"; a failure means "attempted and wrong", and prints both your answer
and the real one. When it prints `71 passed`, you are finished.

Afterwards, read the reference — each script prints its working and asserts
every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_list_versus_array.py
../.venv/bin/python3 02_dtypes_and_overflow.py
../.venv/bin/python3 03_same_answer_faster.py
../.venv/bin/python3 04_creating_and_ufuncs.py
../.venv/bin/python3 05_masks_and_selection.py
../.venv/bin/python3 06_axes_views_and_ranking.py
../.venv/bin/python3 07_nan_and_when_not_to_vectorise.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `vectorize.py` and
`dataset.py` from beside themselves.

Then the full harness:

```bash
bash tests/run_tests.sh
echo "exit=$?"
```

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a virtual environment inside the lab, so nothing here can affect the rest of your machine. `rm -rf .venv` is a complete undo. |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs numpy 2.5.2 and pytest 9.1.1. The one command that uses the network. |
| `.venv/bin/pytest starter -q` | Your running score. Unattempted exercises skip; wrong answers fail with both values printed. |
| `01_list_versus_array.py` | Holds a million integers as a list and as an array, shows the naive `sys.getsizeof` comparison saying they are the same size, explains why that is the wrong measurement, then counts the 28-byte integer objects to get the honest 36,000,056 against 8,000,000. Ends on dtype, shape and strides, and a transpose that copies nothing. |
| `02_dtypes_and_overflow.py` | Adds 1 to 127 in an int8 and gets -128 with no exception and no warning, shows the carry in binary, doubles three int8 values and wraps two of them, shows that a plain Python `1` does not widen the array, and closes on the float32 blind spot at 2^24. |
| `03_same_answer_faster.py` | The spine. Three operations written as a loop and as an expression, compared elementwise over a million values with `==`, then timed five times each with the spread printed and the ratio reported rather than asserted. |
| `04_creating_and_ufuncs.py` | Eight ways to make an array with when to use each, seeded randomness, universal functions against the equivalent comprehension, the `*` versus `@` trap, and the broadcast error message. |
| `05_masks_and_selection.py` | Boolean masking end to end on twenty readings you can count by eye: counting, selecting, combining with `&` and `|`, the ValueError `and` raises, the same error from the missing parentheses, `np.where`, mask assignment, and fancy indexing. |
| `06_axes_views_and_ranking.py` | The axis rule with shapes printed, `np.newaxis` building a full pairwise table, a slice mutating its parent, a table of which operations give a view, `sort` against `argsort`, and Day 103's search ranked with `argsort` and with `argpartition`. |
| `07_nan_and_when_not_to_vectorise.py` | `nan != nan`, `np.isnan`, the nan-aware aggregations — then the honest case against: NumPy losing to a comprehension on four elements, a sequential dependence with no one-line equivalent, and the pairwise table that would need 80 GB. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 107 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 80-check harness: versions, every script, both suites, fifty individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
80 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `107 passed`, and an untouched
starter with `1 passed, 70 skipped`.

Four blocks worth recognising before you meet them. The measurement that looks
like it disproves the lesson:

```
  sys.getsizeof(list)      8,000,056 bytes
  array.nbytes             8,000,000 bytes
  ratio                       1.0000
```

and the same comparison made honestly:

```
  the list's pointers                  8,000,056 bytes
  the integers they point at          28,000,000 bytes
  list total                          36,000,056 bytes
  array total                          8,000,000 bytes
  the array is                              4.50x smaller
```

The spine of the day, from a real run:

```
  scale and offset:  2.5 * x + 1.25
    elementwise identical over 1,000,000 elements : True
    median loop    29.92 ms
    median array   0.243 ms
    speedup        123.2x
```

And the error you will meet on your own within a week:

```
    ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
```

`expected-output/FIELDS.md` records exactly which parts of the captured output
may legitimately differ on your machine — every timing and every ratio, the
platform line, and your own progress score — and which parts may not. It also
explains the one number that looks like a bug and is not: `x ** 0.5` disagreeing
with `np.sqrt` on 1,390 of a million values.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `80 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `107 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `71 passed` once you
   have finished, and never prints a failure you have not been shown.
4. Each of the seven scripts ends with `every assertion held.`
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print` prints
   nothing after a full run.

## Tests

`tests/run_tests.sh` runs 80 checks in seven sections:

1. **Versions** — reads the installed numpy and compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later, which
   two of the dtype claims depend on.
2. **The seven reference scripts** — each must exit 0 and print that every one
   of its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and have
   collected at least a hundred tests, so a collection error cannot pass as
   success.
4. **The starter suite** — must exit 0 on an untouched checkout with skips
   rather than failures; and collecting both suites at once must not turn any of
   those skips into passes, which is a real hazard here because both directories
   contain modules called `vectorize` and `dataset`.
5. **Fifty individual values** — both memory totals and the ratio, the strides,
   the int8 wrap and the absence of a warning, the three exact agreements over a
   million elements, the twenty-times-faster floor, the nine readings above 50
   and the seven between 30 and 70, both ValueErrors, the axis shapes, the view
   writing through and the copy not, the top three articles by name, and every
   nan result.
6. **A deliberate failure** — the harness re-runs itself with one expectation
   swapped for the belief that the nan-aware mean of `[1, 2, nan, 4]` is 2.5,
   which is what you would get if a missing value simply did not count and the
   divisor stayed at four. It asserts that the re-run exits non-zero and reports
   exactly one failure. A green suite proves nothing until you have watched it
   go red.
7. **A clean disk** — no `__pycache__` and no `.pytest_cache` outside `.venv`,
   and no source file that opens a network connection.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the first two behind; section 7 of the
harness fails if they appear. It deliberately does not look inside `.venv`,
because the bytecode caches shipped with NumPy and pytest are theirs, not yours.

## Troubleshooting

See `troubleshooting.md`. It covers the two wrong-directory import errors, all
three separate causes of the ambiguous-truth-value ValueError, the filter for
missing values that finds nothing, the view that changed an array you were not
looking at, int8 arithmetic going negative, results that move between runs, the
off-by-one axis reading, and the `x ** 0.5` disagreement — all found while
building this lab rather than imagined for the document. It also says plainly
which speedup differences are expected and which would mean something is wrong.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no files,
opens no connection after the one-time install, needs no credentials and no
`sudo`, and all the data is invented. Two points there are worth carrying away:
silent integer overflow is a decades-old class of exploitable bug and NumPy will
hand you one without a murmur; and a view shares memory, so returning
`data[0:100]` to a caller gives them a window onto your array rather than a copy
of it.

## Extension exercises

1. **Find the crossover.** The lab shows NumPy losing on four elements and
   winning enormously on a million. Time both at 10, 100, 1,000 and 10,000
   elements and find where the lines cross on your machine. Then explain why the
   crossover moves when the operation gets more expensive — try `np.exp` instead
   of a multiply.
2. **Break the memory measurement.** `list_bytes` counts each distinct integer
   object once. Build a list where that undercounts badly by holding strings
   rather than integers, and work out what a fair accounting would even mean
   when two strings share storage.
3. **A mask you cannot write as one.** Select the readings that are above 50
   **and** whose immediate predecessor was below 30. You will need to line an
   array up against a shifted copy of itself. Do it without a loop, then decide
   honestly whether the loop would have been clearer.
4. **Top-k at scale.** Generate a hundred thousand random scores and time
   `argsort` against `argpartition` for the top ten. Predict the ratio from what
   each one has to do before you measure it.
5. **Make a view bite you.** Write a function that takes an array, keeps a slice
   of it as "the data I care about", and returns it. Then have the caller modify
   the original and watch the stored slice change underneath. Fix it two ways —
   copying on the way in and copying on the way out — and say which is the
   better default.
6. **The nan you did not put there.** Divide one array by another where the
   second contains a zero. Look at what you get, at what warning is emitted, and
   at whether `np.nanmean` afterwards is doing you a favour or hiding the fact
   that a denominator was zero.

## Navigation

- Previous day: Day 103 — Dot Products and Similarity
- Next day: Day 105 — Transforming Images with Matrices
- Week 15: Linear Algebra I: Vectors and Matrices
- Section: Mathematics, Statistics and Data
