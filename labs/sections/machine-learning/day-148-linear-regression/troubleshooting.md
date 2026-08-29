# Troubleshooting

## `No lab .venv found at .venv/bin/python3`

The harness will not run against whatever Python is on your `PATH`,
because a few figures here are pinned to exact package versions. Build the
environment first:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you deliberately want a different interpreter, the harness honours
`PYTHON` and `PYTEST`:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

Expect version-check failures if those do not match the pins. That is the
harness working, not the harness breaking.

## `import file mismatch` when running pytest

You ran `pytest examples starter` in one invocation. Both directories
contain modules with the same names, so pytest cannot decide which
`regression_lib` a test meant. Run them separately:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so this is documented behaviour rather than a surprise.

## My BMI slope, intercept or R-squared do not match

Check that you passed `scaled=False` to `load_diabetes`. The default
(`scaled=True`) returns every column mean-centred and divided by its
standard deviation times the square root of n — a completely different,
uninterpretable scale, and a different fitted line entirely. `load_bmi_
and_target()` in `regression_lib.py` already does this correctly; if
you are calling `load_diabetes` yourself in a scratch script, check the
argument.

## My leverage-point numbers differ slightly

They should not, on the pinned versions — `leverage_dataset()` and the
added point are both fully deterministic (a fixed seed, a fixed x-value
and y-value for the added point). If your slope-without-the-point does not
round to 1.5196, check you passed `x.reshape(-1, 1)` and not the flat
array — scikit-learn's estimators expect a 2-D feature matrix even for one
predictor, and a flat array raises `ValueError`, not a silently wrong
answer, so this is more likely to surface as a crash than a mismatch.

## My slope-recovery numbers (exercise 2) differ

Read `expected-output/FIELDS.md`. The slope-recovery table is an average
over 200 seeded draws from `numpy.random.default_rng`, and NumPy's
documentation is explicit that `Generator` gives no stream-compatibility
guarantee between versions. What must hold on any version: the mean
absolute error strictly decreases as n grows, and the ratio from n=20 to
n=200 falls in a fairly wide band around one-over-root-ten — exercise 2b
asserts the band, not an exact figure, for exactly this reason.

## The curvature or heteroscedasticity numbers seem "too clean"

They are constructed to be, deliberately. `curved_dataset()` and
`heteroscedastic_dataset()` use a fixed seed specifically so the residual
pattern is unambiguous to look at — a real dataset's curvature or
fanning is rarely this textbook-clean, and part of the point of the lesson
is learning to recognise the *shape* here so you can spot a messier
version of it in real data.

## `LinearRegression` warns about anything

It should not. Unlike `LogisticRegression`, ordinary least squares has a
closed-form solution and does not iterate, so there is no convergence
warning to see in this lab.

## The harness is slow

It should not be. The heaviest step is the slope-recovery table's 1,000
total fits (200 replications at each of five sample sizes, the largest
being 5,000 rows and one feature) — well under a second on the capture
machine. If it is taking noticeably longer, check you built the `.venv` as
documented rather than running against a system Python with a different
BLAS backend.
