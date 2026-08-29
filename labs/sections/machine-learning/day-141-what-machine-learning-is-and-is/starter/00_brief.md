# Day 141 lab brief — What the Number Is Not Telling You

You have never trained a model with a library before today, and this lab
is deliberately not a tour of one. Every model here is constructed for
you by a one-line helper in `ml_lib.py` with its settings already fixed,
because the models are not the subject. The subject is what their scores
mean, and what they do not mean.

## The claim you are here to break

> A model that scores well is a model that works.

Exercise 1 destroys it in six lines. A one-nearest-neighbour model
trained on a dataset whose labels are coin flips scores **exactly 1.000**
on its training data — every time, on any machine, by construction,
because each training point is its own nearest neighbour at distance
zero. Its test accuracy is chance. The model has learned nothing and
reports perfection.

Once you have measured that, every other exercise is a variation on the
same discipline: name the number, name what it was measured on, and name
what would have to be true for it to mean anything.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see three passes (the
   machinery checks in `test_ml_lib.py`) and ten skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact datasets, the exact helpers and the exact values to
   assert. None of it is guesswork.
4. Print the measured pair in every exercise. A number you did not print
   is a number you did not look at.
5. When you want to see the whole measured table at once, run
   `.venv/bin/python examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `ml_lib.py`, `test_ml_lib.py` and `test_ml_claims.py`; pytest
aborts on the module-name collision. Run them separately, always.

## What `ml_lib.py` gives you

| Helper | What it is |
| --- | --- |
| `HandwrittenNearestNeighbour` | 1-NN written from first principles in NumPy — eleven lines of arithmetic, no library |
| `pure_noise_dataset` | Normal features, coin-flip labels. No function exists to be approximated |
| `rule_dataset(n, seed, offset)` | Two uniform features, labelled `x1 > x0`. `offset` translates the region without changing the rule |
| `exact_rule` | That same rule, as three lines of code that need no data |
| `flip_labels` / `noisy_rule_dataset` | An exact count of labels flipped, so the noise ceiling is exact arithmetic |
| `checkerboard_dataset` | A clean but intricate boundary — the variance-limited problem |
| `imbalanced_noise_dataset` | 90 percent one class, features pure noise — the baseline trap |
| `quadratic_curve` | One feature, `y = x squared` — the interpolation/extrapolation demonstration |
| `one_nn`, `shallow_tree`, `deep_tree`, `smooth_knn`, `linear_classifier`, `majority_baseline`, `knn_regressor`, `linear_regressor` | Fixed-hyper-parameter model constructors |
| `fit_score` | Fit on train, score on test. Nothing else |
| `should_use_ml`, `problem` | Exercise 9's decision function and its case helper |

Every dataset takes an explicit seed and uses
`numpy.random.default_rng(seed)`, so the numbers in the skip texts are
the numbers you will measure.
