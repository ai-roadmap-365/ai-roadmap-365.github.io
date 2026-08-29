# The ten exercises

Work through these in order. Predict the answer to each `answers.py`
question *before* running anything — the ratio in exercise 1 and the
variance-non-additivity in exercise 5 only catch you if you commit to a
guess first.

Check yourself as you go:

```bash
.venv/bin/pytest starter -q
```

Unattempted work reports as **skipped**, never failed. Wrong work **fails**
with your answer printed beside the correct one.

## 1. The pmf of a sum (`distributions.py`)

`dice_sum_pmf()`, built by enumerating all 36 outcomes of two dice with
`itertools.product` and counting how many land on each sum. Return exact
`fractions.Fraction` values. Assert `pmf[7] == Fraction(1, 6)` and that 7 is
exactly six times as likely as 2 or 12.

## 2. The cdf as a running total (`distributions.py`)

`cdf_from_pmf(pmf)`. Assert it is monotone non-decreasing, ends at exactly
1, and that `cdf[7] - cdf[6] == pmf[7]` exactly.

## 3. Expectation and variance (`distributions.py`)

`expectation_pmf(pmf)` and `variance_pmf(pmf)`, computed from the
definition. Compared in the reference script against a large seeded
simulation using `numpy.random.default_rng` and the standard library's
`statistics` module.

## 4 and 5. Linearity and non-additivity (`distributions.py`)

`expectation_over`, `variance_over` and `covariance_over` — three general
tools that work over any equally-weighted finite space. Let X be the first
die and Y the sum of both dice; Y depends on X directly. Assert
`E[X+Y] == E[X] + E[Y]` exactly (exercise 4), then assert `Var[X+Y] !=
Var[X] + Var[Y]` but `Var[X+Y] == Var[X] + Var[Y] + 2*Cov(X,Y)` exactly
(exercise 5).

## 6. Jensen's inequality (`distributions.py`)

Using the same three tools on a single die: assert `E[X^2] > (E[X])^2`
exactly, and that the gap equals `Var[X]` exactly.

## 7. An inverse-CDF sampler for a discrete pmf (`sampling.py`)

`sample_discrete_inverse_cdf(pmf, rng, size)`, written from scratch with
one uniform draw per sample and `numpy.searchsorted` against the pmf's own
cdf. Assert the empirical frequencies match the pmf within a tolerance
derived from the standard error of a proportion, and that the same seed
reproduces identical draws.

## 8. The exponential distribution from scratch (`sampling.py`)

`sample_exponential_scratch(rate, rng, size)` as `-ln(U) / rate`. Compared
against `Generator.exponential` on sample mean, and with a max-gap
statistic between the two empirical cdfs that you also write by hand
(`empirical_cdf_at`, `max_gap_statistic`) — scipy is not installed, so no
`ks_2samp`.

## 9. Poisson as a Binomial limit (`distributions.py`)

`binomial_pmf(n, p, k)`, `poisson_pmf(lam, k)` and
`max_binomial_poisson_gap(n, p, lam, ks)`. With lambda held at 2 and p =
lambda / n, assert the maximum pmf gap decreases monotonically as n grows
across 10, 100, 1,000 and 10,000.

## 10. A density that exceeds 1 (`distributions.py`)

`uniform_density(x, low, high)` and `numeric_integral(f, low, high,
steps)`. For Uniform(0, 0.5), assert the density equals exactly 2 while its
numeric integral over the support equals 1 to a small tolerance.
