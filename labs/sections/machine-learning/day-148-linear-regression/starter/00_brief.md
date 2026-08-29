# Day 148 lab brief — One Line, Measured

Everybody has seen a fitted line drawn through a scatterplot. Rather fewer
people can read the slope off in real units, say what the four assumptions
behind it are, or tell from a residual plot when the line is quietly
wrong.

This lab measures all of that on one predictor, one target, one line.

## The claim you are here to measure

> A slope is a real-unit statement, and it is only interpretable in real units.

Exercise 1 fits BMI against one-year diabetes-progression score, in the
dataset's *raw* units — not the mean-centred, unit-scaled default scikit-learn
ships, which throws away exactly the interpretability this lesson is
about.

| quantity | measured |
| --- | --- |
| slope | 10.2331 |
| intercept | −117.7734 |
| R-squared | 0.3439 |
| slope standard error | 0.6738 |
| 95% confidence interval | [8.9125, 11.5538] |

In one sentence a clinician could read: **each additional unit of BMI is
associated with about ten more points of one-year disease progression**,
give or take about 0.67 either way — and that slope sits roughly fifteen
standard errors from zero, which is not a borderline effect.

Two facts about that line hold on *any* dataset, exactly, forever, not
just this one: it passes through the point `(mean(x), mean(y))`, and its
residuals sum to zero. Exercise 1c measures both to floating-point
precision.

## The part that should worry you a little

A line can pass every glance-test — a clean scatterplot, a respectable
R-squared — and still be wrong in a way only the residuals reveal.

Exercise 3 fits a line to genuinely curved data. **The R-squared is
0.852.** That looks like a good fit. But bin the residuals by x and they
trace the missed curve exactly: positive at both ends, negative in the
middle. A quadratic curve explains over a third of the residuals' own
variance — a whole model's worth of structure the line called "noise".

Exercise 4 does the same with **heteroscedasticity**: noise whose spread
grows with x. The R-squared is 0.5723, also perfectly ordinary-looking.
The residual standard deviation more than doubles from the low half of x
to the high half — a fan shape invisible in the scatterplot and in the
single number, visible immediately in a residual plot.

Exercise 7 closes the loop: run the same quadratic-fit-to-residuals check
on the *real* BMI model, and it comes back at 0.0002 — essentially zero.
That contrast is how you tell "there is a missed curve" from "there is
just noise".

## The four assumptions, and what breaks each one

| Assumption | What breaks it, in this lab |
| --- | --- |
| Linearity | Exercise 3: a quadratic relationship fitted with a straight line |
| Constant variance (homoscedasticity) | Exercise 4: noise that grows with x |
| No point dominates the fit | Exercise 5: one point out of forty-one changes the slope by more than 85 percent |
| Roughly normal residuals | Exercise 7: a skewness check, and what "roughly" means in practice |

Exercise 5 is the one that should alarm you most. Forty ordinary points,
an unremarkable linear relationship — add one point far out on x with a
y-value that does not follow the trend, and the slope drops from 1.5196
to 0.2138. The mechanism has a name and a number: **leverage**, computed
from the point's x-value alone, before its y-value is even considered.
The added point's leverage is almost 27 times the average of the other
forty.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see four passes (the
   machinery checks in `test_regression_lib.py`) and twelve skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. Print the measured pair in every exercise. A number you did not print
   is a number you did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `regression_lib.py`, `test_regression_lib.py` and
`test_regression_claims.py`; pytest aborts on the module-name collision.
Run them separately, always.

## One scope note

This lab fits exactly one predictor at a time with scikit-learn's
`LinearRegression`. It never derives *why* squared error is the thing to
minimize (Day 149), never adds a second predictor (Day 150), and never
implements ordinary least squares from first principles (Day 153). The
question here is narrower and comes first: given a fitted line, what does
it actually tell you, and how do you catch it lying to you.
