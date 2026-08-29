# Day 103 lab — Which Question Are You Asking?

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Dot Products and Similarity
- **Day number:** 103 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-103-dot-products-and-similarity
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-103-dot-products-and-similarity` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 99 gave you Euclidean distance and it worked well enough that it was easy
to miss what it was actually measuring. This lab breaks it on purpose, in one
number.

Take the roast-chicken article and write it again at twice the length — every
count doubled, same subject, same emphasis. Measure the distance from the
original to its own doubled copy: **9.0554**. Now measure the distance from the
original to race-day-nutrition, an article that is mostly about running:
**8.0623**. Euclidean distance says an article's own doubled copy is further
away than a genuinely different article is.

Nothing is wrong with the arithmetic. The question was wrong. "How far apart
are these two points" is not the same question as "are these two things about
the same subject", and for text they have different answers.

So you build the measure that asks the right question. Seven functions in pure
Python — dot product, norm, normalise, Euclidean distance, cosine similarity,
cosine distance, and a ranking — checked against NumPy on every pair in the
catalogue. Then you use them to prove five things, each of which is asserted
rather than asserted-at:

1. Cosine similarity between an article and its doubled copy is exactly **1.0**.
2. The sign of the dot product tells you the angle: positive under 90 degrees,
   zero at exactly 90, negative above.
3. On **normalised** vectors, ranking by cosine and ranking by Euclidean
   distance produce the identical order — which is why a vector database
   normalises on the way in and then uses whichever is faster.
4. Cosine distance is **not a metric**: it fails the triangle inequality, on a
   concrete triple of two-dimensional vectors you can check on paper.
5. As the number of dimensions grows, random vectors become nearly orthogonal
   and distances bunch up — measured, with a seeded generator, from dimension
   2 to dimension 8192.

And in between, you write a working semantic search over the six articles and
assert its top result for two queries. It is four lines. That is not a
simplification for teaching; that is the retrieval step of a real system, and
everything a production one adds is about getting better vectors and searching
more of them faster.

## Learning objectives

By the end of this lab you can:

1. Reproduce, from real numbers, the case where Euclidean distance calls an
   article's own doubled copy further away than a different article — and
   explain why the distance between `v` and `2v` is exactly `|v|`.
2. Implement `dot`, `l2_norm`, `normalise`, `euclidean_distance`,
   `cosine_similarity` and `cosine_distance` from first principles in pure
   Python, and assert each against NumPy to a stated tolerance.
3. State what `a · b = |a| |b| cos θ` means geometrically, compute the scalar
   and vector projection of one vector onto another, and explain why the
   projection is not symmetric even though the dot product is.
4. Read the sign of a dot product as an angle: positive, zero, negative.
5. Explain why cosine similarity is magnitude-free by construction, and
   demonstrate it by scaling either vector and watching the answer not move.
6. Derive `|u - v| = sqrt(2 - 2 cos θ)` for unit vectors, and use it to explain
   why the two measures rank identically on normalised vectors and can disagree
   on raw ones.
7. Produce a triple where cosine distance fails the triangle inequality, and
   say what breaks in a search index when a "distance" is not a metric.
8. Build a working semantic search from a cosine ranking, and defend the
   tie-breaking rule that makes it deterministic.
9. Measure the curse of dimensionality — falling mean absolute cosine, and
   concentrating distances — with a seeded generator, and say what it changes
   about reading a similarity score.
10. Say when Euclidean distance is the **right** choice, and give an example
    where magnitude carries meaning.

## Prerequisites

- **Day 99** — vectors, components, the L2 norm, unit vectors, normalisation
  and Euclidean distance. This lab uses the identical six-article catalogue.
- **Day 101** — the dot product computed mechanically. Today it gets its
  geometric meaning.
- **Day 70** — floating point, which is why every comparison here declares a
  tolerance and why `cosine_similarity` clamps.
- **Days 71 to 74** — pytest, used for both the reference suite and the running
  score.
- **Day 43** — `python3 -m venv` and installing a package with `pip`.
- No mathematics beyond school arithmetic. Every number in this lab can be
  re-derived with a pen.

## Supported operating systems

- **macOS** — the authoring machine, macOS 26.5.2 on Apple Silicon (arm64).
  Everything in this README was run there.
- **Linux** — the same commands, unchanged. Not run here, so it is stated as
  an expectation rather than a result.
- **Windows** — the Python is identical; the shell is not. `tests/run_tests.sh`
  is a bash script and needs bash, which Windows Subsystem for Linux and Git
  Bash both provide. Inside WSL the instructions are the Linux instructions.
  Paths differ (`.venv\Scripts\python.exe` rather than `.venv/bin/python3`).
  None of this was tested here.

## Hardware requirements

Anything that runs Python. The largest thing this lab allocates is a pair of
2000-by-8192 float arrays in section 7 — about 250 MB peak — and it frees them
between dimensions. If that is too much on your machine, reduce `PAIRS` or drop
the last entry of `DIMENSIONS` in
`examples/07_curse_of_dimensionality.py`; the shape of the result does not
depend on either. No GPU. No internet after the one install.

## Required software

| Tool | Version used here | Purpose |
| --- | --- | --- |
| Python | 3.14.0 | Everything. |
| numpy | 2.5.2 | The independent check on your arithmetic, and the seeded generator. |
| pytest | 9.1.1 | The reference suite and your running score. |
| bash | 3.2.57 | `tests/run_tests.sh`. |

Those are the versions this lab was actually run on. Nothing else was tested,
so nothing else is claimed.

## Free and open-source options

Every tool here is free and open source, and there is no paid tier of anything
involved.

| Tool | Licence | Cost | Account needed |
| --- | --- | --- | --- |
| Python | PSF licence | Free | No |
| numpy | BSD 3-Clause | Free | No |
| pytest | MIT | Free | No |
| bash | GPL | Free | No |

One package is **described but not installed**: `scipy.spatial.distance`, which
provides `cosine`, `euclidean` and about twenty other distance functions and is
what you would reach for in real work. It is not in `requirements.txt`, it was
not run here, and this lab reproduces no output from it. SciPy is BSD-licensed
and free; installing it is one line if you want to compare, but then the
comparison is yours, not this lab's.

## Installation

From this directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. That install is the only time this lab touches the network.

## File structure

```
day-103-dot-products-and-similarity/
├── README.md                     this file
├── metadata.yml                  how the lab was run, and what it printed
├── security.md                   what the lab does to your machine, and what embeddings expose
├── troubleshooting.md            every symptom hit while building this lab
├── requirements/
│   ├── README.md                 why each package is here, and why numpy is pinned
│   └── requirements.txt          numpy==2.5.2, pytest==9.1.1
├── starter/                      YOUR WORK
│   ├── 00_brief.md               read this first
│   ├── similarity.py             seven functions to write
│   ├── answers.py                24 predictions to make
│   ├── test_starter.py           your running score
│   └── conftest.py               the import guard — do not delete
├── examples/                     the reference implementation
│   ├── catalogue.py              the Day 99 articles, unchanged, plus the queries
│   ├── similarity.py             the answer key for starter/similarity.py
│   ├── 01_the_length_confound.py the failure the day exists to fix
│   ├── 02_dot_product_and_sign.py  the geometric meaning, projection, and the sign
│   ├── 03_from_scratch_vs_numpy.py  every pair checked against NumPy, and three edges
│   ├── 04_same_ranking_on_the_sphere.py  the identity, and the rankings matching
│   ├── 05_not_a_metric.py        the triangle inequality failing
│   ├── 06_semantic_search.py     the four-line search
│   ├── 07_curse_of_dimensionality.py  the measurement
│   ├── test_reference.py         76 tests over every claim above
│   └── conftest.py               the import guard — do not delete
├── expected-output/              captured from real runs, never fabricated
│   ├── 01-the-length-confound.txt … 07-curse-of-dimensionality.txt
│   ├── reference-tests.txt
│   ├── starter-progress.txt
│   ├── test-run.txt
│   └── FIELDS.md                 what may differ on your machine, and what may not
└── tests/
    └── run_tests.sh              the harness: 49 checks
```

## How to run

Read `starter/00_brief.md`, then work through `starter/similarity.py` and
`starter/answers.py`, checking yourself as you go:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that reports `1 passed, 51 skipped`. Anything you have
not written is skipped, not failed. When everything is written it reports
`52 passed`.

Then read the reference, in order, from inside `examples/`:

```bash
cd examples
../.venv/bin/python3 01_the_length_confound.py
../.venv/bin/python3 02_dot_product_and_sign.py
../.venv/bin/python3 03_from_scratch_vs_numpy.py
../.venv/bin/python3 04_same_ranking_on_the_sphere.py
../.venv/bin/python3 05_not_a_metric.py
../.venv/bin/python3 06_semantic_search.py
../.venv/bin/python3 07_curse_of_dimensionality.py
cd ..
```

Then the whole thing:

```bash
bash tests/run_tests.sh
```

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a virtual environment inside the lab, so nothing here can affect the rest of your machine. |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs numpy 2.5.2 and pytest 9.1.1. The only network access in the lab. |
| `.venv/bin/pytest starter -q` | Your running score. Unwritten exercises are skipped; wrong answers fail with both numbers printed. |
| `.venv/bin/pytest examples -q` | The 76-test reference suite, asserting every claim the lesson makes. |
| `01_the_length_confound.py` | Reproduces the failure: 9.0554 against 8.0623, then cosine returning exactly 1.0. |
| `02_dot_product_and_sign.py` | `a · b = |a| \|b\| cos θ` from both directions, the projection on a 3-4-5 triangle, five sign cases, and the three orthogonal pairs in the catalogue. |
| `03_from_scratch_vs_numpy.py` | Fifteen pairs checked against NumPy, three equivalent routes to the same cosine, and three edges: the zero vector, rounding past 1.0, and mismatched lengths. |
| `04_same_ranking_on_the_sphere.py` | Derives and checks `\|u - v\| = sqrt(2 - 2 cos θ)`, then ranks the catalogue both ways and shows the orders identical — and shows them differing on raw vectors. |
| `05_not_a_metric.py` | The triangle inequality failing for cosine distance and holding for Euclidean, on the same triple. |
| `06_semantic_search.py` | The four-line search, two queries, and a demonstration that the query's own length changes nothing. |
| `07_curse_of_dimensionality.py` | Mean absolute cosine and distance concentration from dimension 2 to 8192, seeded. |
| `bash tests/run_tests.sh` | 49 checks over all of the above, including one that deliberately breaks the harness to prove it can fail. |

## Expected output

Every file in `expected-output/` was captured from a real run on the authoring
machine on 2026-08-16. The three numbers the day rests on, from
`01-the-length-confound.txt`:

```
  roast-chicken vs its own doubled copy
      [9, 0, 1, 0] - [18, 0, 2, 0] = [-9, 0, -1, 0]
      squares: 81 + 0 + 1 + 0 = 82
      sqrt(82) = 9.0554

  roast-chicken vs race-day-nutrition
      [9, 0, 1, 0] - [4, 6, 3, 0] = [5, -6, -2, 0]
      squares: 25 + 36 + 4 + 0 = 65
      sqrt(65) = 8.0623
```

```
  cos(roast-chicken, its doubled copy)   = 1.0000000000
  cos(roast-chicken, race-day-nutrition) = 0.5514330137
```

The ranking equivalence, from `04-same-ranking-on-the-sphere.txt`:

```
  rank  by cosine (high first)           sim   by distance (low first)         dist
  ---------------------------------------------------------------------------------
  1     roast-chicken               1.000000   roast-chicken               0.000000
  2     slow-cooker-stew            0.990992   slow-cooker-stew            0.134220
  3     race-day-nutrition          0.551433   race-day-nutrition          0.947172
  4     household-budget            0.219512   household-budget            1.249390
  5     marathon-plan               0.011908   marathon-plan               1.405768
  6     storm-bulletin              0.000000   storm-bulletin              1.414214

  the two orders are identical : True
```

The metric failure, from `05-not-a-metric.txt`:

```
  going the long way round : d(a, b) + d(b, c) = 0.292893 + 0.292893 = 0.585786
  going direct             : d(a, c)            = 1.000000
  is direct <= long way?   : False
```

The search, from `06-semantic-search.txt`:

```
  "roast it"
      1. roast-chicken         0.9939
      2. slow-cooker-stew      0.9701
      3. race-day-nutrition    0.5121

  "training for a race and what to eat"
      1. race-day-nutrition    0.9035
      2. marathon-plan         0.9011
      3. roast-chicken         0.3691
```

The curse, from `07-curse-of-dimensionality.txt`:

```
   dimension   mean |cos|     exact  sqrt(2/(pi d))   max |cos|   mean angle  sd of angle  within 10 deg
  ------------------------------------------------------------------------------------------------------
           2       0.6435    0.6366          0.5642      1.0000        88.65        52.23          11.1%
           3       0.5015    0.5000          0.4607      0.9997        90.20        39.07          16.9%
           8       0.2891    0.2910          0.2821      0.9107        89.73        21.55          36.0%
          32       0.1400    0.1422          0.1410      0.5664        90.41        10.10          67.1%
         128       0.0712    0.0707          0.0705      0.3214        89.98         5.09          95.1%
         512       0.0351    0.0353          0.0353      0.1625        90.04         2.52         100.0%
        2048       0.0179    0.0176          0.0176      0.0856        90.00         1.29         100.0%
        8192       0.0089    0.0088          0.0088      0.0394        90.00         0.64         100.0%
```

And the final line of the harness:

```
49 checks, 0 failure(s).
```

`expected-output/FIELDS.md` lists exactly which parts of these files may
legitimately differ on your machine and which may not.

## Validation steps

1. `.venv/bin/python3 -c "import numpy; print(numpy.__version__)"` prints
   `2.5.2`.
2. `.venv/bin/pytest examples -q` reports `76 passed`.
3. `.venv/bin/pytest starter -q` reports `1 passed, 51 skipped` before you
   start, and `52 passed` when you have finished.
4. Each of the seven scripts in `examples/` ends with the line
   `<name>.py: every assertion held.` and exits 0.
5. `bash tests/run_tests.sh` ends with `49 checks, 0 failure(s).` and exits 0.
   Check the exit status directly, not through a pipeline:
   ```bash
   bash tests/run_tests.sh; echo "exit=$?"
   ```
6. Section 6 of that run reports that a deliberately wrong expectation makes
   the harness exit non-zero. If section 6 passes, section 5 is not decorative.
7. `git status` shows nothing untracked in the lab beyond `.venv/` and your own
   edits to `starter/`.

## Tests

`tests/run_tests.sh` runs 49 checks in seven sections:

| Section | What it proves |
| --- | --- |
| 1 | The installed numpy matches the pin, and is version 2 or later. |
| 2 | All seven reference scripts exit 0 and report every internal assertion holding. |
| 3 | The reference pytest suite passes, with at least 70 tests collected. |
| 4 | The starter suite skips unattempted work rather than failing it — **and** the skip count is unchanged when both suites are collected together, which is the check that proves the import guard still works. |
| 5 | Twenty of the lesson's claims, each read as a real value from a real run: the two distances, the cosine of 1.0, agreement with NumPy across every pair, the three sign cases, both ranking results, the unit-sphere identity, the triangle-inequality failure, both search results, the scale invariance, the zero-vector refusal, the clamp, and the dimensionality measurement. |
| 6 | The harness can fail. It re-runs itself with the ranking-equivalence expectation inverted and asserts that the re-run exits non-zero and reports exactly one failure. |
| 7 | Nothing was left behind: no `__pycache__`, no `.pytest_cache`, and no source file that opens a network connection. |

Assertions are on shapes and values, never on timings. Nothing in this lab
asserts a millisecond figure, because such a test is flaky on someone else's
machine.

## Cleanup

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv                # optional: removes the lab virtual environment
git checkout -- starter/    # optional: resets your work
```

The harness leaves nothing behind on its own — section 7 checks — but a script
you ran by hand without `PYTHONDONTWRITEBYTECODE=1` will leave `__pycache__`
directories.

## Troubleshooting

`troubleshooting.md` covers every symptom hit while building this lab,
including the two that cost the most time:

- **`ValueError: math domain error` from `math.acos`** — your
  `cosine_similarity` is not clamping. Three of the six articles miss exact 1.0
  when compared with themselves, and `race-day-nutrition` comes out at
  `1.0000000000000002`, which `acos` refuses. This is measured here, not
  hypothetical.
- **`pytest starter` reporting passes for exercises you have not written** —
  the `conftest.py` import guard is missing or edited. Both directories contain
  a module called `similarity`, and without the guard a combined run measures
  the reference solution.

## Security notes

Full detail in `security.md`. In short: this lab computes and prints, opens no
network connection after the one `pip install`, needs no credentials and no
`sudo`, writes nothing outside its own directory, and cleans up after itself.

Two points that are specific to today and are worth carrying beyond it. First,
an embedding is a fingerprint of the document it came from — a vector derived
from a person's text is derived from a person's text, and similarity search
over it can link documents back to their author whether or not a name was ever
stored. Second, the seeded generator in section 7 is reproducible **by design**
and must never be used where unpredictability is the requirement; for tokens,
passwords, keys and nonces, use `secrets`.

## Extension exercises

1. **Make it fail the other way.** Construct two vectors where cosine
   similarity is high and the two documents are obviously about different
   things. Hint: cosine reads direction only, so a very short document about
   one thing and a very long one about the same thing plus much else can score
   deceptively well. What does that tell you about using cosine alone for
   relevance?
2. **Soft cosine.** Plain cosine treats every feature as unrelated to every
   other, so "cooking" and "baking" would be orthogonal even though they are
   nearly synonyms. Add a 4-by-4 feature-similarity matrix and compute
   `q^T S d / sqrt(q^T S q · d^T S d)`. Check it reduces to plain cosine when
   `S` is the identity — that check is the point of the exercise.
3. **Measure the normalise-once saving.** Time a thousand cosine similarities
   computed from raw vectors against a thousand dot products of pre-normalised
   ones. Report the ratio, on your machine, and say what the number would have
   been if you had asserted a millisecond figure instead.
4. **Break the index.** Write a tiny pruning search that uses the triangle
   inequality to skip candidates, run it with Euclidean distance and then with
   cosine distance on the same data, and find a query where the cosine version
   returns the wrong answer. That is the practical cost of "not a metric".
5. **Push the curse further.** Extend the dimensionality table down to
   dimension 1 and up as far as your memory allows. At dimension 1 the mean
   absolute cosine is exactly 1 — every pair is either parallel or opposite.
   Check that the exact formula predicts it.
6. **Negative components.** The six articles are counts, so nothing is
   negative and no pair can be more than 90 degrees apart. Generate vectors
   with negative components, confirm that cosine distances above 1 now appear,
   and say what a negative similarity would mean if these were real
   embeddings.

## Navigation

- Previous day: Day 102 — Linear Transformations
- Next day: Day 104 — NumPy: Arrays and Vectorized Thinking
- Week 15: Linear Algebra I: Vectors and Matrices
- Section: Mathematics, Statistics and Data
