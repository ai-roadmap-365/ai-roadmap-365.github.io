# Day 151 lab brief — What the Penalty Does

Day 145 already measured that a ridge penalty rescued an overfit
degree-24 polynomial by a factor of 39,588, and that a penalty raises
training error while lowering the variance of what the model learns.

That day treated "regularization" as one thing. It is not. This lab
measures the contrast between the two most common penalties — L2 (ridge)
and L1 (lasso) — on the same dataset, with the same alphas, so the
difference is not a claim you take on faith.

## The claim you are here to measure

> Ridge shrinks. Lasso shrinks and selects. The difference is not a
> matter of degree — it is a difference in shape, and the shape has a
> geometric reason.

Exercise 1 puts the two side by side on `sklearn.datasets.load_diabetes`,
sweeping alpha from 0.001 to 1.0:

| alpha | lasso zeros | lasso R2 | ridge zeros | ridge R2 |
| --- | --- | --- | --- | --- |
| 0.001 | 0/10 | 0.3588 | 0/10 | 0.3586 |
| 0.01 | 1/10 | 0.3541 | 0/10 | 0.3567 |
| 0.1 | 3/10 | 0.3550 | 0/10 | 0.3690 |
| 1.0 | 8/10 | 0.2782 | 0/10 | 0.3570 |

Read the ridge column first. **It never moves.** Zero coefficients at
every alpha tried, from barely-there to aggressive. Ridge shrinks
everything toward zero and never quite arrives.

Now read the lasso column. It climbs steadily to 8 of 10 coefficients
zeroed. Lasso is doing feature selection, not just shrinkage — and it is
doing it as a side effect of the penalty shape, not because anyone told
it which features matter.

## Why: the geometry, made numeric

Exercise 8 builds the smallest case that shows the mechanism: two
strongly correlated features (correlation 0.9999) and an ordinary
least-squares solution of `[1.9564, 1.9381]`. As alpha grows:

| alpha | ridge | lasso |
| --- | --- | --- |
| 0.001 | `[1.9564, 1.9381]` | `[1.9583, 1.9352]` |
| 3.0 | `[1.9507, 1.9141]` | `[0.8919, 0.0]` |
| 8.0 | `[1.9345, 1.882]` | `[0.0, 0.0]` |

At alpha=3.0, lasso's second coefficient is **exactly** 0.0 — not small,
not rounded, exactly zero — while ridge's is still 1.91. That is the
corner of the L1 constraint region landing on an axis. A diamond has
corners on its axes; a circle (ridge's constraint region) does not
touch an axis except at a single tangent point that requires infinite
penalty to reach. Sections "How it works" and the architecture diagram
in the lesson walk through why the shape of the constraint region
forces this.

## What that buys you, and what it costs you

**Exercise 3** confirms lasso does not merely shrink toward *some*
sparse answer — on `make_regression` with a known set of 5 informative
features out of 20, it recovers precisely that set (precision 1.0,
recall 1.0) at a sensible alpha. **Exercise 3b** is the honest half:
push the alpha too high on noisy data and lasso can zero out the truth
entirely (recall drops to 0.0). More penalty is not free precision.

**Exercise 4** is the one with the most practical consequence. The same
alpha, on the same data, in three different units — raw measurement
units, standardized to unit variance, and scikit-learn's own bundled
convention (unit L2 norm) — selects **10, 7, and 3 features
respectively**. The penalty lives in whatever units the coefficients
happen to be in. Skip the scaling step and you have not actually
regularized anything meaningful; you have penalized whichever feature
happened to have small natural units.

**Exercise 6** connects straight back to Day 150's multicollinearity: on
two near-duplicate columns, ridge splits the combined weight roughly
evenly between them (each gets about half); lasso picks one and zeros
the other, arbitrarily as far as the data is concerned.

**Exercise 7** is the practical cost of the shape: ridge is one
linear-algebra call (no `n_iter_` attribute at all); lasso is solved
iteratively — coordinate descent — because its penalty is not
differentiable at zero and no closed form exists.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see four passes (the
   machinery checks in `test_regularization_lib.py`) and fourteen skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip
   text names the exact helper and the exact value to assert.
4. Print every measured pair. A number you did not print is a number you
   did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `regularization_lib.py`, `test_regularization_lib.py` and
`test_regularization_claims.py`; pytest aborts on the module-name
collision. Run them separately, always.

## The scope of this lab

This lab does not re-teach that regularization trades variance for
bias — Day 145 measured that. It does not build linear regression from
scratch — Day 148 and Day 149 own that. It does not cover which metric
to report — Day 152 owns that. It measures exactly one thing in depth:
what the L1 and L2 penalty shapes do differently, and why.
