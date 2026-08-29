# Troubleshooting — Day 141 lab

## `No lab .venv found at .venv/bin/python3` and the harness exits 2

The harness refuses to run against an environment it cannot verify.
Create the lab-local environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you would rather use an interpreter you already have, point the
harness at it — but it must have the pinned versions, and check 1 will
tell you if it does not:

```bash
PYTHON=/path/to/python PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `import file mismatch` when running pytest

You ran `pytest starter examples` in one invocation. Both directories
contain `ml_lib.py`, `test_ml_lib.py` and `test_ml_claims.py`, and
pytest cannot import two different files under the same module name.
Run them as two commands:

```bash
.venv/bin/pytest starter -q
.venv/bin/pytest examples -q
```

Check 7 of the harness verifies this failure still happens, so you can
see it rather than take it on faith.

## `ModuleNotFoundError: No module named 'ml_lib'`

You ran pytest from inside `starter/` or `examples/`, or from the
repository root. Run it from the lab directory, naming the directory:

```bash
cd labs/sections/machine-learning/day-141-what-machine-learning-is-and-is
.venv/bin/pytest starter -q
```

pytest inserts the test file's own directory on `sys.path` (rootdir
inference), which is what lets `import ml_lib` resolve.

## A number is off in the last decimal place

Check your versions first:

```bash
.venv/bin/pip list | grep -E "numpy|scikit-learn"
```

Every value in this lab is deterministic given `numpy` 2.5.2,
`scikit-learn` 1.9.0 and the seeds baked into `ml_lib.py`. A different
scikit-learn can break a tie differently — a decision tree choosing
between two equally good splits, a nearest-neighbour search choosing
between two equidistant points — and shift an accuracy by a fraction of
a point. That is not a bug in your work; it is a version difference, and
`expected-output/FIELDS.md` says exactly which of these numbers are
version-sensitive in that way.

If your versions match and a number still differs, you have found
something worth reporting. Print the whole array, not just the score.

## `test_01` fails with `assert 1.0 == 0.518`

You have swapped the training and test sets. The perfect 1.000 belongs
to the training set — the one the model memorised — and 0.518 belongs to
the 1000 unseen rows. Getting this backwards is the mistake the whole
day exists to prevent, so it is worth pausing on rather than fixing
quickly.

## `ConvergenceWarning` from logistic regression

You should not see one: `linear_classifier()` sets `max_iter=1000` and
the problems here are small and separable. If you do see it, you have
changed a dataset — a much harder or much larger problem may need more
iterations. Raise `max_iter` rather than ignoring the warning; a model
that has not converged is not the model you think you are scoring.

## The harness reports failures in section 2 but pytest passes

Section 2 reproduces the nine claims directly, without pytest, precisely
so that a passing pytest run is never the only evidence. If the two
disagree, trust section 2 and look at what your test is actually
asserting — the most common cause is a test that asserts on a variable
it never recomputed.

## Everything passes but `__pycache__` keeps reappearing

That is normal: Python writes it on every import. The harness clears it
on the way out, and the cleanup commands in `metadata.yml` clear it too.
It is never committed.
