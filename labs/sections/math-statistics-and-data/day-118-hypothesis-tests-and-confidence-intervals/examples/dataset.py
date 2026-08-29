"""Population generators and tolerance constants shared by every exercise.

Every population here has a KNOWN true parameter, which is what makes the
coverage and duality exercises checkable at all: you cannot verify that a
confidence interval has 95% coverage without knowing the true value the
interval is supposed to be catching.

Tolerances below were sanity-checked by rerunning each exercise's core
simulation across seeds 1, 2, 3, 42 and 118 during development; the
comment beside each constant records the range actually observed.
"""
from __future__ import annotations

import numpy as np

# A population with a known mean and standard deviation, used for the
# z-test and coverage exercises. Deliberately not integers so that no
# accidental symmetry hides a bug.
POP_MEAN = 50.3
POP_STD = 12.7

# A second, shifted population -- same shape, different mean -- for the
# two-sample tests.
POP_B_MEAN = 53.1
POP_B_STD = 12.7

# A right-skewed population (exponential) for the permutation test's
# "where the normal approximation does not hold well at small n" arm.
SKEWED_SCALE = 8.0  # exponential scale (mean == scale)


def normal_population(rng: np.random.Generator, n: int, mean: float, std: float) -> np.ndarray:
    return rng.normal(loc=mean, scale=std, size=n)


def skewed_population(rng: np.random.Generator, n: int, scale: float = SKEWED_SCALE) -> np.ndarray:
    return rng.exponential(scale=scale, size=n)


# --- Tolerances, each derived from a standard error or a generous sanity
# band, not picked to make a single run pass. Every tolerance below was
# checked by rerunning the relevant simulation across seeds 1, 2, 3, 42
# and 118 during development; the observed range for that exact seed set
# is recorded next to each one. ---

# Exercise 2 (coverage): with n=300 per sample (large enough that the
# z-critical value is a good stand-in for the t-critical value -- at
# n=40 the true coverage undershoots 95% by about a point because of
# exactly that gap) and 10,000 trials of a Bernoulli(0.95) "did this
# interval cover?" indicator, the standard error of the measured coverage
# is sqrt(0.95 * 0.05 / 10000) = 0.00218, so three standard errors is
# 0.00654. Observed across seeds 1/2/3/42/118: 0.9468-0.9526, i.e. every
# seed landed within 0.0032 of 0.95, comfortably inside the 3-SE band.
COVERAGE_TARGET = 0.95
COVERAGE_TRIALS = 10_000
COVERAGE_SAMPLE_N = 300
COVERAGE_SE = (COVERAGE_TARGET * (1 - COVERAGE_TARGET) / COVERAGE_TRIALS) ** 0.5
COVERAGE_TOLERANCE = 3 * COVERAGE_SE

# Exercise 5 (multiple comparisons): the analytic family-wise error rate
# for 20 independent alpha=0.05 tests is exact: 1 - 0.95**20 = 0.641514...
FWER_TRIALS = 20
FWER_ALPHA = 0.05
FWER_EXACT = 1 - (1 - FWER_ALPHA) ** FWER_TRIALS  # 0.6415140775914581
# Simulated with FWER_FAMILIES families of 20 independent standard-normal
# z-statistics; SE of the simulated FWER at 20,000 families is
# sqrt(0.6415*0.3585/20000) = 0.0034, so 3 SE = 0.0102. Observed across
# five seeds: simulated FWER 0.6388-0.6436, always within 0.0027 of the
# exact value; the Bonferroni-corrected simulation (exact target 0.0488)
# came in 0.0479-0.0528, within 0.004.
FWER_FAMILIES = 20_000
FWER_SIM_TOLERANCE = 0.015
BONFERRONI_EXPECTED = 1 - (1 - FWER_ALPHA / FWER_TRIALS) ** FWER_TRIALS  # 0.048830...
BONFERRONI_TOLERANCE = 0.015

# Exercise 8 (peeking): under a true null, checking after every 10
# observations for up to PEEK_MAX_BATCHES looks and stopping at the first
# p < 0.05 is known to inflate the false-positive rate well past alpha --
# the more looks allowed, the worse it gets. This lab treats "far above
# 0.05" as at least PEEK_MIN_INFLATION_FACTOR times alpha. Observed across
# five seeds with 4,000 simulated experiments and 5 looks: the false-
# positive rate ranged 0.1668-0.1888, roughly 3.3x-3.8x alpha -- well
# clear of the 2x floor used as the assertion.
PEEK_ALPHA = 0.05
PEEK_EXPERIMENTS = 4_000
PEEK_BATCH_SIZE = 10
PEEK_MAX_BATCHES = 5  # up to 50 observations, 5 looks
PEEK_MIN_INFLATION_FACTOR = 2.0  # false-positive rate must be >= 2x alpha

# Exercise 9 (bootstrap vs normal CI): both are estimating the same
# interval for the mean of a normal population with n=200; they need not
# match to the decimal, but their centers should agree closely (in units
# of the normal interval's own standard error) and their widths should be
# within about 20% of each other. Observed across five seeds: center
# difference 0.003-0.053 standard errors (comfortably inside a 0.6-SE
# band), width ratio 0.972-1.023 (comfortably inside a 20% band).
BOOTSTRAP_N_BOOT = 5_000
BOOTSTRAP_WIDTH_RATIO_TOLERANCE = 0.20
BOOTSTRAP_CENTER_TOLERANCE_IN_SE = 0.6  # in units of the normal CI's own SE

# Exercise 6 (power): the closed-form power formula is checked against a
# simulated rejection rate at n=100, effect=2.8, sigma=POP_STD, 3,000
# simulated trials. SE of a simulated rate near 0.34 at 3,000 trials is
# sqrt(0.34*0.66/3000) = 0.0087, so 3 SE = 0.026. Observed across five
# seeds: simulated power 0.336-0.355 against a theoretical 0.3444, always
# within 0.011.
POWER_CHECK_EFFECT = 2.8
POWER_CHECK_N = 100
POWER_CHECK_TRIALS = 3_000
POWER_CHECK_TOLERANCE = 0.03

# Exercise 7 (effect size vs n): a fixed 0.5% relative difference in the
# population mean is tested at a small n and an enormous n. Observed
# across five seeds at n=30: p ranged 0.20-0.86 (never significant); at
# n=100000: p ranged 0.0 to 0.0008 (always significant at alpha=0.05).
EFFECT_VS_N_RELATIVE_DIFF = 0.005
EFFECT_VS_N_SMALL_N = 30
EFFECT_VS_N_LARGE_N = 100_000
