# The nine exercises

Work through these in order. Predict the answer to each `answers.py` question
*before* running anything — the two that catch almost everyone (the
addition-rule error amount and de Méré's favourable bet) only catch you if
you commit to a guess first.

Check yourself as you go:

```bash
.venv/bin/pytest starter -q
```

Unattempted work reports as **skipped**, never failed. Wrong work **fails**
with your answer printed beside the correct one.

## 1. The sample space (`probability.py`)

Write `sample_space_two_dice()` with `itertools.product`, `event()` to
filter a space by a predicate, and `probability()` to return the exact
`Fraction` of an event. Assert `P(sum == 7) == Fraction(1, 6)` — not
`0.16666...`, the exact fraction.

## 2. The addition rule (`probability.py`)

`addition_rule(p_a, p_b, p_a_and_b)` and `naive_sum(p_a, p_b)`. Verify on
`A = "sum is 7"`, `B = "first die is 6"` that the naive sum is wrong by
exactly `P(A and B)`.

## 3. De Méré, exact and simulated (`probability.py`, `simulate.py`)

`complement()` and `at_least_one()` collapse both of de Méré's bets to one
line each. Then `simulate_at_least_one_six()` and
`simulate_at_least_one_double_six()` confirm both by simulation, within a
tolerance derived from the standard error of a proportion.

## 4. Independence (`probability.py`)

`is_independent(p_a, p_b, p_a_and_b)`. Confirmed against one genuinely
independent pair of dice events and one genuinely dependent pair.

## 5. Mutual exclusivity implies dependence

Uses `conditional()` from exercise 6 on a pair of mutually exclusive events.
No new function — the point is what the existing tools reveal.

## 6. Conditioning by restriction (`probability.py`)

`conditional(p_a_and_b, p_b)`. Computed by formula and by literally filtering
the sample space down to the rows where the condition holds; both must agree
exactly.

## 7. The law of total probability (`probability.py`)

`total_probability(priors, conditionals)`, checked against a direct
enumeration of the combined two-urn experiment.

## 8. Monte Carlo error scaling (`simulate.py`)

`simulate_sum_seven()`, called at four sample sizes four decades apart,
averaged over twenty seeds at each. The error should shrink like
`1/sqrt(n)`, not `1/n`.

## 9. Reproducibility (`simulate.py`)

The same `numpy.random.default_rng(seed)` gives byte-identical results
across two calls; a different seed gives a different but still-close result.
