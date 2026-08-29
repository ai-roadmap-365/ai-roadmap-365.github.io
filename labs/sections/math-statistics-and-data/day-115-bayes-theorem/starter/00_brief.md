# The nine exercises

Work through these in order. Predict the answer to each `answers.py`
question *before* running anything — the two that catch almost everyone
(the opening posterior, and the naive-versus-correlated gap in exercise 7)
only catch you if you commit to a guess first.

Check yourself as you go:

```bash
.venv/bin/pytest starter -q
```

Unattempted work reports as **skipped**, never failed. Wrong work **fails**
with your answer printed beside the correct one.

## 1. The opening posterior (`bayes.py`)

Write `posterior(prior, sensitivity, specificity)` in exact `Fraction`
arithmetic. Assert the 99%/99%-test, 1-in-1000-prevalence case gives exactly
`99/1098` (about `0.0902`) — and, as its own assertion, that it is **not**
`0.99`, the answer almost everyone gives.

## 2. Natural frequencies

No new function. Read `dataset.py`'s 100,000-person table (`TP`, `FP`,
`TN`, `FN`) and confirm `TP / (TP + FP)` equals exercise 1's formula answer
exactly — the same arithmetic, just counted instead of multiplied.

## 3. Simulation (`simulate.py`)

`simulate_population(rng, n, prevalence, sensitivity, specificity)` draws a
population of `n` people, tests each one, and counts the four outcome
cells. At `n = 2,000,000`, the empirical `TP / (TP + FP)` should land within
three standard errors of the exact posterior.

## 4. The prevalence sweep (`bayes.py`)

Reuses `posterior()`. Confirm it is strictly increasing across
`dataset.PREVALENCE_SWEEP`, and that at a prevalence of `1/2` it equals
*exactly* `0.99` — the number everyone wrongly gives for the 1-in-1,000
case, now the actual right answer for a different base rate.

## 5. The odds form (`bayes.py`)

`probability_to_odds()`, `odds_to_probability()`, `likelihood_ratio()` and
`update_odds()`. Assert `posterior_odds == prior_odds * likelihood_ratio`
exactly, and that converting back to a probability matches exercise 1's
direct answer.

## 6. Sequential updating (`bayes.py`)

`sequential_posterior(prior, tests)`, applying one likelihood ratio per
test in odds form. Two different tests (A: 99%/99%, B: 95%/98%), both
positive: confirm the posterior, and that updating A-then-B gives the
identical result to B-then-A.

## 7. Correlated tests (`bayes.py`)

`independent_pair_probability()` and `correlated_pair_probability()`. Same
test, run twice on one sample, with a shared failure mode half the time.
Compute the posterior the naive (assumes-independence) way and the correct
(correlation-aware) way, and confirm the naive one is strictly higher —
overstated confidence, not just a different number.

## 8. Naive Bayes with Laplace smoothing (`naive_bayes.py`)

`train()`, `word_probability()` (with an `alpha` smoothing parameter),
`document_score()` and `classify()`. A tiny spam/ham corpus. Confirm correct
classification of two clean held-out documents, and that a third document —
built around one word absent from one class's training data — classifies
correctly *with* smoothing and collapses that class's probability to
*exactly* zero *without* it.

## 9. Log space (`naive_bayes.py`)

`multiply_probabilities()` and `sum_of_logs()`. Confirm that multiplying
500 factors of `0.01` as plain `float64` underflows to exactly `0.0`, while
the corresponding sum of logs stays finite — the reason a real classifier
is built with `document_log_score()`, not `document_score()`.
