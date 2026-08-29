# Troubleshooting

## `No lab .venv found at .venv/bin/python3`

The harness will not run against whatever Python is on your `PATH`,
because every number here is pinned to exact package versions. Build the
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

## Training error RISES at degree 18 and 24

Expected, asserted, and worth understanding rather than working around.
The training column falls monotonically through degree 14 and then wobbles
upward by 0.0636.

That wobble is **numerical, not statistical**. The training set has 25
rows and degree 24 supplies exactly 25 polynomial features, so the fit is
solving a square and catastrophically ill-conditioned system. Nothing
about learning theory is involved; it is floating-point arithmetic running
out of road.

The lab asserts monotonicity through degree 14 and asserts that it does
*not* hold overall, rather than pretending the curve is clean. If you
remove the `StandardScaler` from `polynomial_model` the effect gets far
worse, which is the machinery test that demonstrates why the scaler is
there.

## The degree-24 model gets WORSE from 15 rows to 25

Also expected, also asserted, and it is exercise 3c. At 25 rows the
number of features equals the number of rows: the system is square, the
solution is unique, it interpolates every training point exactly, and it
is under no constraint whatsoever about what happens between them.

At 15 rows there are more features than rows, the system is
under-determined, and least squares returns the minimum-norm solution —
which is quietly a form of regularisation and behaves far better. The
worst place to be is exactly at the threshold.

## My test error is below my training error

Read exercise 1c. That is a negative generalisation gap and it is the
signature of underfitting, not of a broken split. A model too rigid to
chase noise has none to be flattered by, so its training score carries no
optimism.

It is worth being sure, though: if you see a negative gap on a *flexible*
model, that genuinely is worth investigating, and a duplicated row across
the split is the usual cause.

## The decomposition does not sum exactly

It sums to within 0.0002, and the lab asserts that tolerance rather than
equality. Each part is stored already rounded to four decimal places, so
summing the rounded parts can differ from the rounding of the sum by up to
half a unit in the last place per part.

Separately, the predicted total agrees with the *observed* error to within
1.003 percent at worst. That gap is sampling error in the observed column
— which is a Monte Carlo estimate over 200 models times 200 query points —
not error in the identity. Five of the seven capacities agree to better
than a quarter of a percent.

## My early-stopping epoch differs

The softest number in the lab, and `expected-output/FIELDS.md` says so.
The test curve after its minimum is not monotone: it rises to 7.1435
around epoch 84 and partly recovers to 5.8978 by epoch 600, without ever
again beating the 5.4555 it reached at epoch 14.

What must hold on any version: training error falls at every epoch, the
test minimum is early, and the generalisation gap grows. If your training
error is not monotone, something is genuinely wrong — check that you are
using `partial_fit` and not refitting from scratch each epoch.

## The harness takes a while

It does. The decomposition fits 200 models per capacity across seven
capacities, and the training history runs 600 epochs. On the capture
machine the whole harness completes in well under a minute; on a slower
one it will take several.

No timing is asserted anywhere, so a slow machine changes nothing about
whether it passes. While developing, call the library functions directly
with a smaller `datasets` or `epochs` argument — both are parameters — and
put them back before running the harness.

## `import file mismatch` when running pytest

You ran `pytest examples starter` in one invocation. Both directories
contain modules with the same names, so pytest cannot decide which
`fitting_lib` a test meant. Run them separately:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so this is documented behaviour rather than a surprise.

## `LinAlgWarning` or a conditioning warning at high degree

Possible on some BLAS builds when fitting degree 24 to 25 rows, and it is
telling you the truth: that system is ill-conditioned. It does not affect
any assertion in this lab, and the wobble it produces is measured and
asserted. If you want it silenced, filter it in your own code rather than
in the library — the warning is a real signal and worth keeping.
