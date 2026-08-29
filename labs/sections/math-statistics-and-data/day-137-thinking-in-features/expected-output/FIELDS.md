# What in these captures is exact, and what may differ

Captured from a real run on 2026-08-20, in this lab's own `.venv`, on
pandas 3.0.5, NumPy 2.5.2, pytest 9.1.1, Python 3.14.0, macOS (arm64).
scikit-learn is not installed on this machine, which is why every model
in this lab — a logistic regression trained by gradient descent and a
nearest-centroid classifier — is written out in NumPy.

Three files sit here:

| File | What it is |
| --- | --- |
| `test-run.txt` | The full `bash tests/run_tests.sh` output |
| `examples-run.txt` | `pytest examples -q` |
| `starter-run.txt` | `pytest starter -q` on an untouched checkout |

## Exact everywhere, on any correct install

Every generator in `data.py` uses a seeded `numpy.random.default_rng`,
and every split is seeded too. Nothing is sampled at run time and no
result depends on the clock, the machine or the order the tests run in.
The harness asserts this directly: it calls `data.signups()` twice and
compares the frames, and runs the first experiment twice and compares
the dictionaries.

- `test-run.txt` ends with `55 checks, 0 failure(s)` and exit 0.
  `examples-run.txt` ends with `9 passed`; `starter-run.txt` ends with
  `9 skipped`. The counts are structural — 9 test functions per file,
  55 `check` calls in the harness — and do not depend on the machine.
- **Exercise 5 is exact arithmetic**, not a measurement. Raw hours put
  23 and 0 exactly 23.0 apart. On the circle every adjacent pair sits
  `2*sin(pi/24) = 0.26105238444010315` apart, and the spread across all
  24 adjacent pairs is under 1e-12 — floating point, not statistics.
  Hours 0 and 12 sit exactly 2.0 apart, the circle's diameter.
- The audit flags exactly `days_to_first_invoice` (rule `separable`) and
  `email_template` (rule `pure_category`), and none of `visits`,
  `minutes_on_site`, `discount_pct` or `channel`.
- The numeric leak's absolute correlation with the target is **0.8468**,
  which is *below* the audit's default 0.90 threshold. The correlation
  rule alone would have missed it.

## The before/after pairs, as measured on this machine

| Experiment | Leaky / contaminated | Honest | Gap |
| --- | --- | --- | --- |
| 1. Target leakage | 1.0000 | 0.6400 | 36.0 points |
| 2. Scaler fitted on all data (mean of 200 splits) | 0.6218 | 0.6224 | **−0.06 points** |
| 2. Group-mean imputer fitted on all data (mean of 150 splits) | 0.7484 | 0.6662 | 8.22 points |
| 3. Target encoding, all data vs out-of-fold (mean of 40 splits) | 0.6215 | 0.5535 | 6.80 points |
| 4. Random split vs time-ordered split | 0.8833 | 0.0667 | 81.67 points |
| 8. Vocabulary on all documents vs training only (mean of 40 splits) | 0.8137 | 0.7893 | 2.45 points |

Every one of those numbers is reproducible on any machine with the
pinned versions, because every split is seeded. What is *not* general is
the size of each gap: it is a property of these generators, and a
different dataset will show a different number. The **directions** are
the general result, with one exception described below.

## Four honesty calls, in order of how much they matter

### 1. Contaminating a scaler bought nothing at all — measured

The brief for this lab expected the scaler fitted on all the data to
score higher than the correctly fitted one. Measured over 200 random
splits with a 25-row test set, it scored **0.06 points lower**: 0.6218
against 0.6224. The direction was not merely small, it was reversed.

The reason is arithmetic, not luck. Standardisation applies *one* affine
map to both halves of the data. Contaminating it cannot move the test
rows towards the training rows; all it can change is the relative
weighting of the features, and a logistic regression run to convergence
is very nearly invariant to that. Two further constructions were tried
before this was accepted as the answer, on a two-column lognormal table
of the same shape as `data.pricing()`: equal-width binning with edges
fitted on all data, and a rank transform fitted on all data, each over
300 splits at three training-set sizes. Binning came out **1.9 to 2.7
points in favour of the correctly fitted version**, and the rank
transform came out within half a point either way.

So the lab asserts what is true: a contaminated *scaler* is worth less
than one point in either direction, and a contaminated *group-mean
imputer* — which is not an affine map, and fills each gap from its own
small group — is worth 8.2 points. That is the more useful lesson. Not
all contamination is equal, and the thing that decides how much a leak
is worth is how much the leaking statistic knows.

### 2. The temporal gap is deliberately sharp

0.8833 against 0.0667 is a dramatic number, and it comes from a
deliberately sharp construction: the alarm rate flips between roughly
0.88 and roughly 0.08 from one calibration batch to the next, and the
last batch is held out entirely by the time-ordered split. Real
regime changes are usually milder.

What is not exaggerated is the shape of the failure. The time-ordered
score of 0.0667 is *below* the 0.9333 majority-class baseline for that
period — the model is not merely uninformed about the new batch, it is
confidently wrong about it, because it learned a batch-to-rate mapping
that no longer applies. The harness asserts that comparison directly.

### 3. The vocabulary gap is small and configuration-sensitive

2.45 points, averaged over 40 splits. Eight combinations of `top_k` and
`min_docs` were measured before one was chosen; six of the eight showed
the contaminated vocabulary ahead, by 0.6 to 2.5 points, and two showed
it 0.27 points behind. The shipped configuration (`top_k=30`,
`min_docs=2`) is the largest of them, and the assertion floor is 1.5
points rather than 2.4 for that reason.

The mechanism is real but weak: choosing the vocabulary decides only
which columns *exist*, not what values they take, so it can leak only
through the marginal slots that rare words compete for. Compare that
with the target encoding, where the leaked target goes straight into the
feature's value and the gap is 6.8 points.

### 4. The interaction has a linear escape hatch

Exercise 7 reports income alone at 0.5400, spend alone at 0.6667 and the
ratio at 1.0000. It also reports that a logistic regression given *both*
raw columns reaches 1.0000 as well, and the lab asserts that rather than
hiding it: the boundary in this construction is `spend = 0.5 * income`,
a straight line through the origin, and a linear model can find a
straight line. The ratio is still the feature that states the rule in
one number a person can read, and a distance-based model gets nothing
from the two raw columns.

## What may legitimately differ on another machine

- **Timings.** `pytest examples -q` took 16.34s here. Nothing in the
  lab asserts a duration.
- **The pytest summary line's wording** across pytest versions. The
  harness matches `^9 passed` and `^9 skipped` rather than the whole
  line.
- **The last decimal of a mean over splits**, if NumPy ever changes the
  bit stream of `default_rng` for a given seed. That has not happened
  across the 2.x series, and every assertion is a band rather than an
  equality for exactly this reason — except exercise 5, which is
  arithmetic and is asserted exactly.
- **`import file mismatch`** is the message pytest 9.1.1 prints when
  `pytest examples starter` is run in one invocation. Older pytest
  versions word it differently; the harness matches case-insensitively
  on that phrase, and the run must fail either way.
