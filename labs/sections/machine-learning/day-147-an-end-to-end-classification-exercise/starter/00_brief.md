# Day 147 lab brief — One Classification Project, Run Properly

Days 141 through 146 each isolated one discipline in a lab built to show it
in isolation: what a score means, the three feedback shapes, the workflow's
stage contract, the three sets and the selection optimism they exist to
control, the bias/variance trade, and the scikit-learn estimator API.

This lab is not a new discipline. It is all six of them, spent on one real
dataset, in the order a working project actually uses them: frame,
baseline, split, pipeline, cross-validate, select, **one** test evaluation,
error analysis, an honest verdict with an interval.

## The dataset, chosen by measuring

Three datasets ship inside scikit-learn and need no download: iris, wine
and the Wisconsin breast-cancer set. This lab tries all three before
choosing:

| dataset | rows | features | classes | majority baseline | test rows at 20% |
| --- | --- | --- | --- | --- | --- |
| iris | 150 | 4 | 3 | 0.3333 | 30 |
| wine | 178 | 13 | 3 | 0.3889 | 36 |
| breast_cancer | 569 | 30 | 2 | 0.6316 | 114 |

Iris and wine both saturate near-perfect cross-validated accuracy with a
36-candidate sweep, on a test set of 30 to 36 rows — one wrong answer moves
accuracy by more than two and a half points, which is too coarse for an
honest interval and leaves no room to see selection optimism behave the
way the theory predicts. **This lab uses breast_cancer**: a baseline that
is not trivially beaten, 114 test rows, and 30 real-valued measurements
from a digitised fine-needle aspirate. Exercise 1 asserts the numbers that
justify the choice.

## What the honest run measures

Thirty-six candidate pipelines — 15 k-nearest-neighbours settings, 11
logistic-regression regularisation strengths, 10 decision-tree depths —
are cross-validated five ways on the training rows only. The winner is
`LogisticRegression(C=1)`, at a cross-validated accuracy of **0.9780**.
Fitted on the full training set and evaluated **exactly once** against the
test rows, it scores **0.9825** — a drop of −0.0045, meaning the test score
came out very slightly *better* than the cross-validated one, not worse.

## The number this lab was built to check

Day 144 gave you a formula: the optimism from picking the best of K
candidates is the validation set's standard error times the expected
maximum of K standard normal draws — computable before you run the sweep.
Applied here, with K = 36 and the winner's cross-validated accuracy, it
predicts an optimism of **0.0326**. The measured drop at this seed is
**−0.0045**.

That is not a rounding error. Across 20 independent seeds the mean
measured drop is **−0.0001** — statistically indistinguishable from zero —
against a mean prediction of **0.0330**. The formula overestimates the real
optimism here by more than thirty-fold on average.

**Why**, and it is worth sitting with before exercise 7b: Day 144's
formula assumes K *independent, zero-skill* candidates — literal coin
flips. This lab's 36 candidates are neither. Adjacent `k` values in
k-nearest-neighbours and adjacent regularisation strengths in logistic
regression produce nearly identical predictions, so the *effective*
number of independent choices is far smaller than 36. And every candidate
here has genuine, if varying, skill — the "maximum of noise" framing
does not apply to a maximum taken over real signal. The formula is not
wrong; it is answering a question this sweep does not ask.

## The leak this lab lets you cause on purpose

Exercise 10 rebuilds the mistake Day 144 spent a whole lesson on, in its
most common real form: selecting a model by fitting every candidate and
scoring it **on the test set directly**, instead of selecting on
cross-validated train rows and looking at test once.

At the reported seed the leak costs nothing — a ceiling effect, because
114 test rows can only move accuracy in steps of about 0.88 points. Over
20 seeds it costs a mean of **+0.0096**, up to **+0.0351**, and it is
**never negative** — the leak can only make the reported number look as
good or better than the honest one, never worse. That asymmetry is the
mechanism, not luck.

## Error analysis, before the verdict

The one test evaluation makes two mistakes, both the same kind: two
malignant cases predicted benign. Zero benign cases are predicted
malignant. Accuracy alone — 0.9825 — does not tell you that every error
this model makes is the clinically costlier one.

## The verdict, with an interval

`n_test = 114` gives a standard error of 0.0123 and a 95 percent
half-width of ±0.0241. The interval is `[0.9584, 1.0066]`. The improvement
over the 0.6316 baseline is +0.3509 — comfortably larger than the
interval, so the honest verdict here is **distinguishable, clearly**, not
the "cannot distinguish" verdict Day 144 warned a small test set can force.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see four passes (the
   machinery checks in `test_classification_lib.py`) and fourteen skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `classification_lib.py`, `test_classification_lib.py` and
`test_classification_claims.py`; pytest aborts on the module-name
collision. Run them separately, always.

## And the rule, made mechanical, again

Exercise 6 wraps the test set in the same `GatedTestSet` pattern Day 144
built: exactly one evaluation, `TestSetTouchedTwice` on the second, and a
counter that does not advance on a refused attempt. Nine days in, this is
not a new idea — it is the same discipline, proven on a real dataset
instead of a synthetic one.
