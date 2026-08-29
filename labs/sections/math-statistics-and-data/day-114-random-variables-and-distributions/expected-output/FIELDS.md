# What may legitimately differ on your machine

Captured from real runs on 2026-08-17, macOS, Python 3.14.0, NumPy 2.5.2,
pytest 9.1.1. This file separates exact rational arithmetic (identical on
any correct implementation, anywhere) from sampled figures (which will
differ, within their stated tolerance, on another machine, another NumPy
version, or another run without a fixed seed).

## Exact rational arithmetic -- cannot differ anywhere

Every one of these is computed with `fractions.Fraction` over a finite,
fully enumerated sample space, and is asserted with `==`, never with a
tolerance. If you get a different exact value than these, the code has a
bug -- there is no "close enough" here.

| Quantity | Exact value | Where |
| --- | --- | --- |
| P(two dice sum to 7) | `1/6` | `01_pmf_of_a_sum.py` |
| P(two dice sum to 2) | `1/36` | `01_pmf_of_a_sum.py` |
| ratio, P(sum=7) to P(sum=2) | `6` | `01_pmf_of_a_sum.py` |
| F(7) - F(6) | `1/6` | `02_cdf_from_pmf.py` |
| F(12), the cdf's largest value | `1` | `02_cdf_from_pmf.py` |
| E[Y], Y = sum of two dice | `7` | `03_expectation_and_variance.py` |
| Var[Y] | `35/6` | `03_expectation_and_variance.py` |
| E[X], X = first die alone | `7/2` | `03_expectation_and_variance.py` |
| E[X + Y], X = first die, Y = sum | `21/2` | `04_linearity_with_dependence.py` |
| Var[X], Var[Y] (joint space) | `35/12`, `35/6` | `05_variance_is_not_additive.py` |
| Cov(X, Y) | `35/12` | `05_variance_is_not_additive.py` |
| Var[X + Y] | `175/12` | `05_variance_is_not_additive.py` |
| E[X^2] - (E[X])^2, single die | `35/12` | `06_jensens_inequality.py` |
| Var[X], single die | `35/12` | `06_jensens_inequality.py` |
| Uniform(0, 0.5) density on its support | `2.0` (exact, not sampled) | `10_density_above_one.py` |

## Sampled -- will differ within tolerance on another machine

Every value below comes from `numpy.random.default_rng(114)` (this lab's
fixed seed) or a derived seed. The exact draws are reproducible on any
machine running the same NumPy version with the same seed, but the
comparisons below are checked against a **tolerance**, not an exact
literal, so a different NumPy version's random-number algorithm (unlikely
to change within a major version, but not contractually guaranteed across
one) could shift the specific numbers while leaving every assertion true.

| Quantity | This run | Tolerance | Derivation |
| --- | --- | --- | --- |
| simulated mean of the dice sum (200,000 trials) | 7.00077 | 3 standard errors (~0.0054 x 3) | `sqrt(Var[Y] / n)` |
| empirical frequencies from the inverse-CDF sampler (200,000 draws) | within 0.0009 of exact pmf | 3 standard errors (~0.00083 x 3) | `sqrt(p(1-p) / n)`, worst case over the 11 values |
| from-scratch exponential sample mean (50,000 draws, rate=2) | 0.4982 | 3 standard errors (~0.00224 x 3) | `sqrt((1/rate)^2 / n)` |
| NumPy's own exponential sample mean (same draws, same rng state) | 0.4995 | same as above | same |
| max-gap statistic between the two exponential empirical cdfs | 0.0050 | DKW-derived threshold, 0.01357 | Dvoretzky-Kiefer-Wolfowitz inequality, alpha=0.01, n=50,000 each |
| Binomial(10, 0.2)-vs-Poisson(2) max pmf gap | 0.0313 | strictly decreasing across n | measured, not a fixed target |
| Binomial(10,000, 0.0002)-vs-Poisson(2) max pmf gap | 2.71e-05 | strictly decreasing, and < 0.001 | measured |
| numeric integral of the Uniform(0, 0.5) density | 1.0 (to 6 decimals) | 1e-6 | trapezoid rule, 100,000 panels |

The full captured console output for every reference script, the reference
pytest suite, an untouched starter run, and the complete test harness are
in this directory, one file per script plus `reference-tests.txt`,
`starter-progress.txt` and `test-run.txt`.
