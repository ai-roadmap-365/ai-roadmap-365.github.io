# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the
authoring machine on 2026-08-24: macOS 26.5.2 (Apple Silicon, arm64),
Python 3.14.0, in this lab's own `.venv` built from
`requirements/requirements.txt` — numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, with scipy 1.18.1, joblib 1.5.3 and threadpoolctl 3.6.0
pulled in as scikit-learn's own dependencies.

## Exact on any machine, for any reason

- **`1.000` — 1-NN training accuracy (exercise 1).** This is not a
  measurement in the ordinary sense; it is arithmetic. Every training
  row is its own nearest neighbour at distance zero, so `predict` on the
  training set returns each row's own stored label. It is 1.000 on this
  machine, on yours, under any version of scikit-learn, for any seed and
  any dataset — with exactly one exception, documented below.
- **`0.900` — the majority-class baseline in exercise 6.** The test set
  is constructed with exactly 100 minority rows in 1000, so the fraction
  of class 0 is exactly 0.9 by construction rather than by sampling. The
  harness asserts the construction as well as the score.
- **`0.750` — the noise ceiling in exercise 7.** Exactly 1000 of 4000
  test labels are flipped (`flip_labels` flips a fixed count, not a
  fixed probability), so a model that recovered the underlying rule
  perfectly would score exactly 0.750. The lab asserts the flip count
  directly, so the ceiling is arithmetic, not an estimate.
- **`1.000` — the exact rule's accuracy in exercises 2 and 4.** The rule
  is the same function that produced the labels, so it cannot be wrong
  on data generated that way, on any machine.
- **149 unique feature rows in iris out of 150** — a property of the
  published dataset, identical wherever it is loaded.
- The harness's final line in the shape `N checks, M failure(s)`, with
  `M` zero on green and greater than zero on a genuinely broken suite.
  The check count, 13, is exact for this version of `tests/run_tests.sh`.

## Exact for the pinned versions, and sensitive to them

Every remaining number — 0.518, 0.8855, 0.9675, 0.96, 0.6535, 0.948,
0.4895, 0.180, 139.704, 0.780, 0.7655, 0.821, 0.817, 0.73725, 0.72675,
0.68825, 0.60875, 0.5995, 0.99725, 0.6655, 0.68675 — is reproducible **given the
pins**, and is not guaranteed beyond them. Two independent reasons:

1. **NumPy's `Generator` carries no compatibility guarantee.** The NumPy
   documentation states directly that `Generator` does not provide a
   version compatibility guarantee and that the bit stream may change as
   better algorithms evolve. Seeding makes these datasets identical on
   any machine running numpy 2.5.2; it does not make them identical on
   numpy 3.x. This is worth stating plainly because "we seeded it" is
   routinely offered as if it were sufficient, and it is not.
2. **Tie-breaking inside scikit-learn is an implementation detail.** A
   decision tree choosing between two equally good splits, and a
   nearest-neighbour search choosing between two equidistant points, can
   resolve differently across versions. `DecisionTreeClassifier` is
   constructed with `random_state=141` throughout, which fixes the
   randomness the estimator itself controls, but not the library's
   internal ordering conventions.

Nothing in this lab depends on these values being stable across
versions. If you re-run under different pins and a number moves, the
claim being tested — perfect training accuracy is not evidence, the rule
beats the model, no model crosses the ceiling — is what should still
hold, and the exact assertions are there so that a drift is visible
rather than silent.

## The one exception to "1-NN training accuracy is 1.000"

A 1-NN misses a training row only when an identical feature row carries
a different label, in which case the tie can be broken toward the wrong
one. This is not hypothetical: **iris contains exactly one duplicated
feature row**, at positions 101 and 142, `(5.8, 2.7, 5.1, 1.9)`. Both
carry class 2, so on iris's real labels a 1-NN still scores exactly
1.000. Permute the labels and the same pair drops it to
0.9933333333333333 — 149 of 150. Exercise 1b measures this rather than
asserting the tidier claim, because the tidier claim is false and the
exception is the interesting part.

The measured value `0.9933333333333333` in
`measured-values.txt` depends on which label the permutation assigns to
each of the two duplicated rows, so it depends on the NumPy pin in the
way described above. The exercise asserts only that the score is below
1.000, which is the part that is structural.

## Machine-dependent, and asserted nowhere

- **Wall-clock durations** — `13 passed in 0.61s` in
  `examples-run.txt` and `3 passed, 10 skipped in 0.53s` in
  `starter-run.txt` will differ on every machine and on every run.
  Nothing in this lab asserts on a timing.
- **The last two check lines in `test-run.txt` read "cleaned during
  this run".** They will read that way on a clean checkout too, and this
  is not an oversight: the harness runs pytest three times in sections 3,
  4 and 5 before it reaches the clean-up sweep in section 8, and every
  one of those runs writes `__pycache__` and `.pytest_cache`. The check
  is therefore "is the lab clean when the harness exits", answered by
  removing them and confirming it. Both wordings are `ok:`, both count as
  one check, and the final line is `13 checks, 0 failure(s)` either way.
- **The temporary directory name** in harness check 9-10
  (`mktemp -d` under `$TMPDIR`) differs every run and is never printed.

## Proof the harness can fail

Twice, during authoring:

1. Inside the harness, section 7, on every run: a scratch copy of
   `examples/` is confirmed passing, exercise 1's
   `assert train_acc == 1.0` is rewritten to `0.5`, the suite is
   confirmed to exit non-zero naming
   `test_01_one_nn_scores_a_perfect_1_000_having_learned_nothing`, and
   the scratch directory is removed.
2. By hand, on the real file: `assert test_acc == 0.518` in
   `examples/test_ml_claims.py` was changed to `0.999` and the whole
   harness re-run. It reported `13 checks, 2 failure(s)` and exited 1 —
   the direct check in section 2 and the pytest run in section 3 both
   caught it. The file was restored and the harness returned to
   `13 checks, 0 failure(s)`, exit 0.
