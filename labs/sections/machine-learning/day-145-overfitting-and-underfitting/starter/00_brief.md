# Day 145 lab brief — Two Ways to Be Wrong

There are exactly two ways a model can be wrong, and they are not two ends
of one dial. They are two different quantities, they respond to completely
different interventions, and this lab measures both directly.

## The claim you are here to measure

> Underfitting is bias. Overfitting is variance. They add up, with
> irreducible noise, to the error you actually observe.

That is usually presented as a picture and left alone, because measuring
its terms needs something you never have: many independent training sets
and knowledge of the true function. In a lab you have both.

Exercise 4 fits **200 models to 200 independent training sets**, predicts
the same fixed grid with all of them, and asks two questions. How far is
the *average* prediction from the truth? That is bias. How far do the
individual predictions scatter from their own average? That is variance.

| degree | bias² | variance | noise | predicted | observed |
| --- | --- | --- | --- | --- | --- |
| 1 | 4.2985 | 0.7112 | 4.0000 | 9.0097 | 9.0295 |
| 3 | 0.0033 | 0.8399 | 4.0000 | 4.8432 | 4.8431 |
| 12 | 2803.5354 | 452183.1336 | 4.0000 | 454990.6691 | 455027.8625 |

The last two columns are the point. **The three parts add up to the error
that was actually observed**, at every capacity, to within one percent.
This is an identity, not an analogy, and you are going to check it.

## The measurement that changes what people do

```text
      n    degree 1     degree 4        degree 24
     15      8.5023      4.9218      215413.2388
   2000      8.2393      3.9880           4.0055
```

A hundred and thirty times more data took the overfit model from 215,413
to 4.0055 — which is exactly the irreducible floor — and the underfit
model from 8.5023 to 8.2393.

**More data cures one failure completely and the other not at all.** If
you are about to spend three months labelling, this is the number that
decides whether it is worth it.

## The finding that is easiest to miss

```text
   deg    train MSE        test MSE             gap
     1      11.3217          9.8274         -1.4942
```

The gap is **negative**. The degree-1 model scores better on data it has
never seen than on the data it was fitted to.

That is not a broken split. A model too rigid to chase the noise in its
training set has no noise-chasing to be flattered by, so its training
score carries none of the usual optimism. It is the signature of
underfitting — and an engineer who sees it usually assumes a leak and
applies more regularisation, which is precisely the wrong direction.

## Two things this lab found by accident, and kept

**Degree 2 is worse than degree 1 on both terms.** It contains every
degree-1 model as a special case and still measures more bias (4.3342
against 4.2985) *and* double the variance. The true function is odd, so a
quadratic term buys nothing and still has to be estimated. Capacity is not
a single dial running from worse to better.

**The degree-24 model is worse at 25 training rows than at 15.** Test
error rises by a factor of three hundred, to sixty-four million, before
falling to the floor. Degree 24 supplies exactly **25 features**, so at 25
rows the system is square: one exact interpolating solution, under no
constraint at all about what happens between the points. At 15 rows there
are more features than rows and least squares returns the minimum-norm
solution, which is quietly a form of regularisation. That peak is the
interpolation threshold, and exercise 3c makes you prove it with a feature
count.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see four passes (the
   machinery checks in `test_fitting_lib.py`) and fourteen skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. Print the measured pair in every exercise. A number you did not print
   is a number you did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `fitting_lib.py`, `test_fitting_lib.py` and
`test_fitting_claims.py`; pytest aborts on the module-name collision. Run
them separately, always.

## The exercises

| # | What it establishes |
| --- | --- |
| 1 | Training error falls with capacity; test error is U-shaped and explodes |
| 1b | The training curve stops being monotone where the numerics give out |
| 1c | The SIGN of the gap is the diagnostic — negative means underfitting |
| 2 | A penalty rescues the same model class by a factor of 39,588 |
| 2b | The penalty trades training error for test error, and has its own U-curve |
| 3 | More data cures overfitting and does nothing for underfitting |
| 3b | Two good models converge on the irreducible floor from opposite sides |
| 3c | The overfit column peaks exactly where features equal rows |
| 4 | Underfitting is bias; overfitting is variance |
| 4b | The decomposition predicts the error that was observed |
| 4c | A strictly larger model class can be worse on both terms |
| 5 | Training longer improves training error and worsens the model |
| 5b | The generalisation gap grows fivefold while training error falls |
| 5c | The test curve is not a clean U, which is why patience exists |
