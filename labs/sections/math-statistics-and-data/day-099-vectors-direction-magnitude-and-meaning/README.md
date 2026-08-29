# Day 99 lab — Vectors You Can Hold

Six short articles. Four hand-counted features each. By the end of this lab you
will have written, from nothing, the nine functions that turn "these two
articles are similar" into a number — and you will have proved that your loops
agree with NumPy on every one of them.

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Vectors: Direction, Magnitude, and Meaning
- **Day number:** 99 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-099-vectors-direction-magnitude-and-meaning
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-099-vectors-direction-magnitude-and-meaning` when the site is running.
<!-- generated-links:end -->

## Purpose

A vector is a list of numbers where position means something. That is the whole
definition, and you have been using them since Day 1 without the name: an RGB
colour is a 3-vector, a row in a CSV is a vector, a set of per-user counts is a
vector.

This lab makes the idea operational. You implement addition, subtraction,
scaling, the dot product, both norms, distance, normalisation and
nearest-neighbour search in pure Python — no libraries, just `math.sqrt` and a
loop. Then you run the same operations through NumPy on the same inputs and
assert they agree, so that when you start trusting the library you know exactly
what it is doing for you.

The payoff is a working miniature of semantic search: six articles turned into
vectors by counting words, and a program that answers "which article is most
like this one" with arithmetic you can redo on paper.

Two things get taught the hard way, by demonstration rather than assertion:

- **Never compare floats with `==`.** Normalising a vector gives a magnitude
  that is 1 to within floating-point error. On the authoring machine, three of
  seven test vectors came out at `0.9999999999999999` — including one whose
  original magnitude was exactly `7.0`. A test written with `==` fails on
  correct code, which is the worst kind of failure because it sends you hunting
  for a bug that is not there.
- **"Nearest" is undefined until you name a norm.** The lab contains two
  candidates where the L2 norm says one is nearer and the L1 norm says the
  other is. Both are right. The choice is yours to make and to write down.

## Learning objectives

By the end of this lab you will be able to:

1. Implement componentwise addition, subtraction and scalar multiplication over
   plain Python lists, and refuse a dimension mismatch rather than truncating it.
2. Implement the dot product and explain why it returns a single number.
3. Derive the L2 norm from Pythagoras and implement it, then check it against
   four vectors whose magnitude is a whole number.
4. Implement the L1 norm and state a case where it and L2 disagree about which
   of two candidates is nearer.
5. Compute the distance between two vectors as the magnitude of their
   difference, without learning a separate formula.
6. Normalise a vector, explain what normalising changes and what it preserves,
   and assert the result with a stated tolerance rather than `==`.
7. Turn six documents into vectors by counting features, compute every pairwise
   distance, and name each item's nearest neighbour.
8. Show that raw counts and normalised vectors can pick different winners for
   the same query, and explain why length was competing with topic.
9. Prove that your pure-Python implementation and NumPy agree, operation by
   operation, to a stated tolerance.

## Prerequisites

- **Day 43-46** — Python functions, lists, comprehensions, and floating point.
  Day 46 in particular: this lab is where "never compare floats with `==`" stops
  being advice and becomes a failing test.
- **Day 51** — modules and imports, which is how `examples/` finds `vectors.py`.
- **Day 63** — testing with pytest, and what a parametrised test does.
- **Day 83** — virtual environments and pinned requirements, which is how the
  two dependencies get installed.
- School arithmetic. Squares, square roots, and the fact that a right triangle
  with sides 3 and 4 has a hypotenuse of 5. Nothing beyond that.

## Supported operating systems

- macOS 12 or later, Intel or Apple Silicon. Built and run on macOS 26.5.2,
  arm64.
- Linux, any current distribution with Python 3.10 or later.
- Windows 10 or later. The Python is identical; the paths differ
  (`.venv\Scripts\python.exe` instead of `.venv/bin/python3`). `tests/run_tests.sh`
  is a bash script — run it under Git Bash or WSL, or work through the
  `run_commands` in `metadata.yml` by hand.

## Hardware requirements

Anything that runs Python. The largest object this lab creates is a 3-by-4
array. Disk usage is dominated by NumPy itself, at roughly 30 MB installed.

## Required software

| Software | Version used here | Notes |
| --- | --- | --- |
| Python | 3.14.0 | 3.10 or later is fine; nothing here uses a 3.14-only feature |
| NumPy | 2.5.2 | Pinned in `requirements/requirements.txt` |
| pytest | 9.1.1 | Pinned in `requirements/requirements.txt` |
| bash | 3.2.57 or later | Only to run `tests/run_tests.sh` |

## Free and open-source options

Everything in this lab is free and open source, and there is no paid tier of
anything to consider.

- **Python** — PSF licence, free.
- **NumPy** — BSD-3-Clause, free. There is no commercial edition; the NumPy
  everybody uses is this one.
- **pytest** — MIT, free.

The nine functions you write need no third-party package at all: `math.sqrt`
from the standard library is the only import. NumPy appears here to be checked
against, not to be depended on. That is deliberate — a reader who has written
the loop can read NumPy's documentation and know what it means.

The lesson also discusses PyTorch tensors, JAX arrays and pandas Series.
**None of the three is installed here and no output from them is reproduced
anywhere in this lab.** They are described from their published documentation
and labelled as such. `tests/run_tests.sh` confirms their absence so the claim
cannot quietly rot.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-099-vectors-direction-magnitude-and-meaning
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

That last line should print `2.5.2`. This is the only step that needs a
network connection; everything afterwards runs offline.

If you would rather use an environment you already have, every command below
works with any Python that has NumPy and pytest, and the test harness accepts
overrides:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## File structure

```
day-099-vectors-direction-magnitude-and-meaning/
├── README.md                     this file
├── metadata.yml                  lesson id, commands, how the captured run was made
├── troubleshooting.md            every error message, with its real text
├── security.md                   what the lab touches, and where vectors become a security question
├── requirements/
│   ├── README.md                 why each package is here
│   └── requirements.txt          numpy==2.5.2, pytest==9.1.1
├── starter/                      YOUR WORK GOES HERE
│   ├── 00_brief.md               the scenario, the table of six articles, the trap stated in advance
│   ├── vectors.py                nine numbered exercises; runs and reports progress before you start
│   ├── test_starter.py           12 tests: 1 worked example, 11 skipped until you finish an exercise
│   └── pytest.ini                puts starter/ on the import path
├── examples/                     the reference implementation and five demonstrations
│   ├── vectors.py                all nine functions, pure Python, no NumPy
│   ├── byhand.py                 magnitudes and distances whose answers are whole numbers
│   ├── agreement.py              pure Python against NumPy, operation by operation
│   ├── normalise.py              normalisation, and the == trap it hides
│   ├── norms.py                  where L1 and L2 rank two candidates in opposite orders
│   └── embeddings.py             six articles, every pairwise distance, nearest neighbours
├── tests/
│   ├── test_vectors.py           79 tests against the reference implementation
│   └── run_tests.sh              the harness: 87 checks over everything above
└── expected-output/              captured from real runs, never typed by hand
    ├── FIELDS.md                 what may legitimately differ on your machine
    ├── byhand.txt
    ├── agreement.txt
    ├── normalise.txt
    ├── norms.txt
    ├── embeddings.txt
    ├── starter-progress.txt
    └── test-run.txt
```

## How to run

Read `starter/00_brief.md` first. It has the table of six articles, the four
numbers to check yourself against on paper, and the float trap stated before
you hit it.

```bash
# 1. See where you are. Before you start: 0 of 9.
.venv/bin/python3 starter/vectors.py

# 2. Implement the exercises in starter/vectors.py, in order.
#    After each one, delete its @pytest.mark.skip line in starter/test_starter.py
#    and run the suite again.
.venv/bin/pytest starter -q

# 3. When all 12 pass, compare your reasoning with the reference programs.
cd examples
../.venv/bin/python3 byhand.py       # the arithmetic, shown in full
../.venv/bin/python3 normalise.py    # why == is the wrong test
../.venv/bin/python3 norms.py        # L1 and L2 disagreeing
../.venv/bin/python3 embeddings.py   # the six articles, ranked
../.venv/bin/python3 agreement.py    # your loops vs NumPy
cd ..

# 4. Run the reference suite and then the full harness.
.venv/bin/pytest tests -q
bash tests/run_tests.sh
```

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 starter/vectors.py` | Calls each of the nine exercises with a sample input and prints what came back. Unfinished ones report `not started` rather than crashing, so the file is useful from the first minute |
| `pytest starter -q` | The exercise suite. One worked test passes immediately; eleven are skipped until you delete their `@pytest.mark.skip` line |
| `python3 byhand.py` | Prints five magnitudes and four distances with the full working — the squares, the sum, the square root — next to the value the code produced, and whether they agree. Every answer is a whole number, so you can check all nine with a pen |
| `python3 normalise.py` | Normalises seven vectors and shows, for each, the exact `repr` of the resulting magnitude, whether `== 1.0` holds, and whether `math.isclose` holds. This is the file that makes the float argument concrete |
| `python3 norms.py` | Two candidates and one query, scored under both norms, with the working shown. L2 picks `spread`, L1 picks `spike`, and the second case shows the effect is about the shape of the difference rather than about sitting at the origin |
| `python3 embeddings.py` | The six-article catalogue: the table of features, every pairwise distance, two of those distances worked out in full, each article's nearest neighbour, and a comparison of raw versus normalised ranking for a short query |
| `python3 agreement.py` | Runs eleven operations through your pure-Python code and through NumPy on identical inputs and asserts agreement with `numpy.allclose(rtol=1e-9, atol=1e-12)`. Then shows the two things NumPy adds: measuring every row of a table at once, and broadcasting one query against all of them |
| `pytest tests -q` | 79 tests against the reference implementation |
| `bash tests/run_tests.sh` | The full harness — 87 checks across versions, the reference suite, every example's output, and two deliberate sabotage runs that prove the suites are not vacuous |

## Expected output

Captured from a real run on the authoring machine on 2026-08-16. See
`expected-output/FIELDS.md` for the one line that is legitimately
machine-dependent.

The starter, before you write anything (`expected-output/starter-progress.txt`):

```
Day 099 starter — Vectors You Can Hold

  1. add          not started
  2. subtract     not started
  ...
  9. nearest      not started

0 of 9 exercises return something.
```

Magnitude, worked in full (`expected-output/byhand.txt`):

```
  |[2, 3, 6]|
      = sqrt(2^2 + 3^2 + 6^2)
      = sqrt(4 + 9 + 36)
      = sqrt(49)
      = 7          computed: 7.0   agrees: True
```

The float trap (`expected-output/normalise.txt`):

```
vector                    |v|                   |v_hat| (exact repr)      == 1.0   isclose
------------------------------------------------------------------------------------------
[3, 4]                    5.0                   1.0                       True     True
[1, 1]                    1.4142135623730951    0.9999999999999999        False    True
[2, 3, 6]                 7.0                   0.9999999999999999        False    True

exactly 1.0 : 4 of 7
isclose 1.0 : 7 of 7
```

The two norms disagreeing (`expected-output/norms.txt`):

```
  nearest under L2: spread
  nearest under L1: spike
  the two norms disagree: True
```

The embedding answering its question (`expected-output/embeddings.txt`):

```
  roast-chicken        -> slow-cooker-stew     at 1.4142
  slow-cooker-stew     -> roast-chicken        at 1.4142
  marathon-plan        -> race-day-nutrition   at 5.7446
  race-day-nutrition   -> marathon-plan        at 5.7446
  household-budget     -> race-day-nutrition   at 9.0000
  storm-bulletin       -> marathon-plan        at 10.6771
```

The harness (`expected-output/test-run.txt`), final line:

```
87 checks, 0 failure(s).
```

## Validation steps

1. `.venv/bin/python3 starter/vectors.py` prints `0 of 9 exercises return
   something.` before you begin, and `9 of 9` when you have finished.
2. `.venv/bin/pytest starter -q` reports `1 passed, 11 skipped` before you
   begin, and `12 passed` when you have finished all nine exercises and deleted
   all eleven skip markers.
3. `.venv/bin/pytest tests -q` reports `79 passed`.
4. `cd examples && ../.venv/bin/python3 byhand.py` ends with
   `all exact cases agree: True`.
5. `cd examples && ../.venv/bin/python3 agreement.py` prints
   `every operation agrees: True`.
6. `cd examples && ../.venv/bin/python3 normalise.py` prints
   `isclose 1.0 : 7 of 7` and a first count strictly smaller than 7.
7. `cd examples && ../.venv/bin/python3 embeddings.py` ends with
   `Closest pair in the whole catalogue: roast-chicken and slow-cooker-stew at 1.4142`.
8. `bash tests/run_tests.sh` ends with `87 checks, 0 failure(s).` and exits 0.
   Check the exit status directly — `bash tests/run_tests.sh; echo $?` — rather
   than piping it anywhere, because a pipeline reports the last command's
   status, not the harness's.

## Tests

`tests/run_tests.sh` runs 87 checks in ten sections. It exits 0 only if every
one passes, and non-zero on any failure.

| Section | What it proves |
| --- | --- |
| 1 | The installed NumPy and pytest match the pins, and PyTorch, JAX and pandas really are absent — so the lesson's "described from documentation, no output reproduced" claim stays true |
| 2 | The 79-test reference suite passes; named tests are actually collected; **no test compares a float with `==` or `!=`** except the two whose job is to prove the trap; and both suites state their tolerance explicitly |
| 3 | Every hand-computable magnitude and distance comes out of the code with the value a reader gets on paper |
| 4 | Pure Python and NumPy agree on all eleven operations, with at least fourteen individual `True` results and no `False` |
| 5 | Normalising gives magnitude 1 to tolerance in all seven cases, and **strictly fewer than seven land on exactly `1.0`** — the `==` trap reproduced here rather than being asserted on faith |
| 6 | L1 and L2 rank the same two candidates in opposite orders, in both the origin-centred and the translated case |
| 7 | Every nearest-neighbour answer and every worked distance in the embedding is the one the lesson quotes |
| 8 | The starter runs before any exercise is done, reports its state honestly, and imports no NumPy |
| 9 | **The suites are not vacuous.** The reference implementation is dropped in as the student's answer and all 12 starter tests go green; then the square root is removed from `l2_norm` and the suite goes red naming the right test; then `subtract` is swapped for `add` inside `distance` and `tests/` goes red naming the right test |
| 10 | No `.venv`, `.pytest_cache`, `out/` or `__pycache__` left behind, and no lab source opens a socket |

Section 9 is the one worth reading. A test suite that cannot tell a finished
implementation from a broken one is decoration, and the only way to know is to
break something on purpose and watch it fail. This harness does that twice, on
throwaway copies in `mktemp -d` directories that it removes afterwards. The
originals are never touched.

## Cleanup

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv                # optional: removes the lab virtual environment
git checkout -- starter/    # optional: reset your work
```

The harness sets `PYTHONDONTWRITEBYTECODE=1` and disables pytest's cache, so a
clean run leaves nothing behind. The first two lines are for tidying up after
running pytest yourself without those flags.

## Troubleshooting

See `troubleshooting.md`. It covers the missing-NumPy error, the harness's
tool-resolution failure, the `NoneType has no len()` cascade when exercises are
done out of order, the dimension-mismatch and zero-vector refusals (both
working as intended), NumPy's silent `nan` where this lab raises, and the
Windows path differences. Every message quoted there was produced on purpose
while building this lab.

## Security notes

See `security.md`. In short: this lab reads and writes nothing, opens no
socket, needs no privileges, and writes only inside two `mktemp -d` directories
it removes. The only network step is the one-off `pip install`.

That file also covers where vector work genuinely does become a security
question — embeddings are not anonymised data, a vector database is a database,
nearest-neighbour rankings leak the existence of documents a user may not be
allowed to see, and a similarity threshold compared with `==` is a decision an
attacker can nudge.

## Extension exercises

1. **Cosine similarity.** The dot product of two unit vectors is a similarity
   score between −1 and 1. Add `cosine_similarity(u, v)` to `vectors.py`,
   implemented as `dot(normalise(u), normalise(v))`, and check it against
   `embeddings.py`: the score between `roast-chicken` and `slow-cooker-stew`
   should be close to 1, and between a cooking article and `storm-bulletin`
   close to 0. Then prove the connection: show that for unit vectors, the
   squared distance equals `2 - 2 * cosine_similarity(u, v)`.
2. **A seventh article.** Invent one, count its four features by hand, add it to
   `CATALOGUE`, and predict its nearest neighbour before you run the code. Being
   wrong is the useful outcome — work out which component drove the answer.
3. **Chebyshev distance.** Implement the L-infinity norm: the largest absolute
   component, with no sum at all. Find a pair of candidates where it disagrees
   with both L1 and L2. Three norms, three answers, all correct.
4. **Break the tolerance.** In `starter/test_starter.py`, change `REL_TOL` to
   `1e-18` and run the suite. Which tests fail, and are those failures telling
   you about your code or about floating point? Then set it to `1e-1` and ask
   which real bugs would now get through. The lesson is that a tolerance is a
   decision with two failure modes, not a magic number.
5. **Scale it up.** Generate 10,000 random 300-dimensional vectors with NumPy,
   and find the nearest neighbour to a query using (a) your pure-Python loop and
   (b) one broadcast NumPy expression. Time both with `time.perf_counter`.
   Report the ratio you measure on your machine rather than a number you read
   somewhere — and note that the answers must agree to tolerance, or the speed
   is worthless.
6. **The zero-vector policy.** This lab raises on `normalise([0, 0, 0])` while
   NumPy returns `nan`. Write down which behaviour you would want in a document
   ingestion pipeline that processes a million files unattended, and defend it.
   There is a real argument on both sides.

## Navigation

- Lab brief and exercises: `starter/00_brief.md`
- Reference implementation: `examples/vectors.py`
- Captured runs: `expected-output/`
- Section index: `../README.md`
- Previous lab, the last day of the preceding section:
  `../../programming-with-python/day-098-section-project-a-complete-data-pipeline/`
- Next lab, once it is published, sits beside this one under `../`. This is the
  first day of the Mathematics for AI subsection, so there is no earlier lab in
  this directory.
