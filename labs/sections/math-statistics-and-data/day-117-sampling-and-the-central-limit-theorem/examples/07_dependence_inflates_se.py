"""Exercise 7 -- dependence inflates the true standard error, quietly.

Generate an autocorrelated AR(1) series -- each observation is 0.7 times the
previous one plus fresh noise, so consecutive observations are far from
independent. Measure the TRUE standard error of its sample mean the only
honest way: generate many independent replications of the whole series and
look at the spread of their means. Compare that against the NAIVE standard
error, sample_std / sqrt(n), which assumes independence the data does not
have.

The naive formula should understate the true standard error -- meaningfully,
not by a rounding error -- which is worse than an honest formula being
merely imprecise: it makes the analyst confident in exact proportion to how
wrong they are.
"""

import dataset as D
from sampling import ar1_series, naive_standard_error, true_standard_error_by_replication
import numpy as np

rng = np.random.default_rng(7)

true_se = true_standard_error_by_replication(D.AR1_N, D.AR1_PHI, D.AR1_SIGMA, D.AR1_REPLICATIONS, rng)

# The naive SE is reported as an average over many single series, since any
# one series' sample standard deviation is itself noisy.
naive_ses = [
    naive_standard_error(ar1_series(D.AR1_N, D.AR1_PHI, D.AR1_SIGMA, rng))
    for _ in range(500)
]
naive_se_avg = float(np.mean(naive_ses))

ratio = true_se / naive_se_avg

print(f"AR(1) series: n = {D.AR1_N}, phi = {D.AR1_PHI}, sigma = {D.AR1_SIGMA}")
print(f"TRUE standard error (from {D.AR1_REPLICATIONS} independent replications) = {true_se:.4f}")
print(f"NAIVE standard error (sample_std / sqrt(n), averaged over 500 series) = {naive_se_avg:.4f}")
print(f"ratio (true / naive) = {ratio:.2f}")
print()
print("An analyst who trusted the naive formula here would report a confidence "
      "interval that is too narrow -- not slightly, but by a factor that a "
      "single glance at the ratio above makes obvious.")

assert ratio > D.AR1_INFLATION_FLOOR, (
    f"the naive SE was not meaningfully smaller than the true SE (ratio = {ratio:.2f}, "
    f"expected above {D.AR1_INFLATION_FLOOR})"
)

print("07_dependence_inflates_se.py: every assertion held.")
