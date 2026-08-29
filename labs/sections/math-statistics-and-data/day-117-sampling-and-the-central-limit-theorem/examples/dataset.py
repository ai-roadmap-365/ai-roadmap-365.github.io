"""Every population, parameter and trial count used anywhere in this lab.

All data here is invented and deterministic: every population is generated
once, at import time, from `numpy.random.default_rng(DATASET_SEED)`. Nothing
is read from a file and nothing touches the network. If you want a different
population, change a parameter here and every script and test downstream
picks it up automatically.
"""

import numpy as np

DATASET_SEED = 117

_rng = np.random.default_rng(DATASET_SEED)

# ---------------------------------------------------------------------------
# Populations. POP_SIZE stands in for "the population" -- large enough that
# sampling from it with replacement behaves like sampling from the true
# infinite population to every decimal place this lab checks.
# ---------------------------------------------------------------------------

POP_SIZE = 200_000

# A skewed population: waiting-time shaped, heavily right-tailed. This is the
# population exercises 1, 2, 3 and 5 build the sampling distribution from.
SKEWED_SCALE = 3.0
SKEWED_POP = _rng.exponential(scale=SKEWED_SCALE, size=POP_SIZE)

# A biased coin: values are 0 or 1, P(1) = 0.2, so the population itself is
# skewed in the opposite direction from SKEWED_POP -- used in the lesson to
# show the CLT working on a population that is not just skewed but discrete
# with only two possible values.
COIN_P = 0.2
COIN_POP = (_rng.random(POP_SIZE) < COIN_P).astype(float)

# A lumpy, two-spike population: two clusters far apart with a little noise
# around each, and nothing in between -- about as far from bell-shaped as a
# population can look while still having finite variance. The two spikes
# carry UNEQUAL weight (80/20) so the population itself is genuinely skewed,
# not merely bimodal -- an equal-weight version is symmetric and has zero
# skewness already, which would make it useless for exercise 3's monotone-
# decrease check.
TWO_SPIKE_CENTERS = (-5.0, 5.0)
TWO_SPIKE_WEIGHTS = (0.8, 0.2)
TWO_SPIKE_NOISE = 0.4
_spike_choice = _rng.choice(TWO_SPIKE_CENTERS, size=POP_SIZE, p=TWO_SPIKE_WEIGHTS)
TWO_SPIKE_POP = _spike_choice + _rng.normal(0.0, TWO_SPIKE_NOISE, size=POP_SIZE)

# ---------------------------------------------------------------------------
# Exercise 1 -- the sampling distribution itself
# ---------------------------------------------------------------------------

EX1_N = 40
EX1_TRIALS = 20_000

# ---------------------------------------------------------------------------
# Exercise 2 -- the sqrt(n) law
# ---------------------------------------------------------------------------

SQRT_N_LAW_NS = (10, 40, 160, 640)
SQRT_N_LAW_TRIALS = 20_000
# Each successive n is exactly 4x the one before it, so the standard error
# should shrink by a factor of exactly sqrt(4) = 2 each step. Simulation noise
# keeps the measured ratio from landing on 2.000 exactly; this tolerance was
# checked across seeds 1, 2, 3, 42, 117 and 999 before being fixed here, and
# the worst observed ratio across those runs was 1.98.
SQRT_N_LAW_RATIO_TOLERANCE = 0.25

# ---------------------------------------------------------------------------
# Exercise 3 -- the CLT's skewness signature
# ---------------------------------------------------------------------------

SKEW_DEMO_NS = (2, 5, 20, 80, 320)
SKEW_DEMO_TRIALS = 50_000

# ---------------------------------------------------------------------------
# Exercise 4 -- the Cauchy counterexample
# ---------------------------------------------------------------------------

CAUCHY_DEMO_TRIALS = 20_000
CAUCHY_DEMO_N_SMALL = 10
CAUCHY_DEMO_N_LARGE = 1_000
EXPONENTIAL_SCALE = 1.0
# From n=10 to n=1000 the sample size grows 100x, so a finite-variance mean's
# spread should shrink by close to sqrt(100) = 10x. Checked across six seeds,
# the exponential ratio never fell below 9.7; 8.0 leaves comfortable margin
# while still ruling out "did not shrink".
EXPONENTIAL_SHRINK_FLOOR = 8.0
# The Cauchy mean's spread should NOT shrink at all -- checked across the same
# six seeds, the ratio stayed within 0.98-1.03. A factor-of-3 band in either
# direction is generous and still miles from the exponential's ~10x.
CAUCHY_NO_SHRINK_LOW = 1.0 / 3.0
CAUCHY_NO_SHRINK_HIGH = 3.0

# ---------------------------------------------------------------------------
# Exercise 5 -- bias does not shrink
# ---------------------------------------------------------------------------

BIAS_DEMO_TRIALS = 5_000
BIAS_DEMO_N_SMALL = 30
BIAS_DEMO_N_LARGE = 3_000
# Same 100x growth in n as the Cauchy exercise. The unbiased sampler's mean
# absolute error should shrink by close to 10x; checked across six seeds the
# ratio stayed in 9.8-10.3, so a floor of 7 is comfortable.
UNBIASED_SHRINK_FLOOR = 7.0
# The biased sampler's error should stay roughly flat. Checked across six
# seeds the ratio (error at n=30 / error at n=3000) stayed within 0.99-1.00;
# a band of 0.4-2.5 is generous and still clearly distinguishes "flat" from
# the unbiased sampler's ~10x drop.
BIASED_FLAT_LOW = 0.4
BIASED_FLAT_HIGH = 2.5

# ---------------------------------------------------------------------------
# Exercise 6 -- the bootstrap, from scratch
# ---------------------------------------------------------------------------

BOOTSTRAP_SAMPLE_SIZE = 200
BOOTSTRAP_SAMPLE_MEAN = 50.0
BOOTSTRAP_SAMPLE_STD = 10.0
BOOTSTRAP_N_BOOT = 5_000
# The bootstrap standard error of the MEAN has a closed form to check against
# (sigma_hat / sqrt(n)), so this tolerance can be tight: checked across six
# seeds, the relative error never exceeded 0.7%.
BOOTSTRAP_MEAN_RELATIVE_TOLERANCE = 0.15
# The MEDIAN has no closed form. "Sane" here means: within a generous factor
# of the spread of medians computed from genuinely fresh independent samples
# of the population. Checked across six seeds, the ratio of the two spreads
# stayed within 0.57-1.11; a factor of 3 in either direction leaves room for
# the small-sample noise inherent in estimating a spread of a spread.
BOOTSTRAP_MEDIAN_SANITY_LOW = 1.0 / 3.0
BOOTSTRAP_MEDIAN_SANITY_HIGH = 3.0
FRESH_MEDIAN_REPLICATIONS = 2_000

# ---------------------------------------------------------------------------
# Exercise 7 -- dependence inflates the true standard error
# ---------------------------------------------------------------------------

AR1_N = 200
AR1_PHI = 0.7
AR1_SIGMA = 1.0
AR1_REPLICATIONS = 3_000
# Checked across six seeds, true_se / naive_se stayed within 2.34-2.46 for
# this (phi, n) combination, so a floor of 1.5 leaves a wide, safe margin
# while still requiring a real, meaningful understatement.
AR1_INFLATION_FLOOR = 1.5

# ---------------------------------------------------------------------------
# Exercise 8 -- the evaluation-margin calculation
# ---------------------------------------------------------------------------

EVAL_ACCURACY = 0.914
EVAL_N = 500
EVAL_EXPECTED_SE_PCT = 1.25  # percentage points, to 2 decimal places
EVAL_SE_TOLERANCE_PCT = 0.05
EVAL_MARGIN_PCT = 0.3

# ---------------------------------------------------------------------------
# Exercise 9 -- reproducibility
# ---------------------------------------------------------------------------

REPRO_N = 40
REPRO_TRIALS = 2_000
REPRO_SEED_A = 7
REPRO_SEED_B = 8
