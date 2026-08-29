"""Every population, parameter and trial count used anywhere in this lab.

This file is complete and does not need editing -- your work for each
exercise lives in `sampling.py`. All data here is invented and deterministic:
every population is generated once, at import time, from
`numpy.random.default_rng(DATASET_SEED)`. Nothing is read from a file and
nothing touches the network.
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
# not merely bimodal.
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
EXPONENTIAL_SHRINK_FLOOR = 8.0
CAUCHY_NO_SHRINK_LOW = 1.0 / 3.0
CAUCHY_NO_SHRINK_HIGH = 3.0

# ---------------------------------------------------------------------------
# Exercise 5 -- bias does not shrink
# ---------------------------------------------------------------------------

BIAS_DEMO_TRIALS = 5_000
BIAS_DEMO_N_SMALL = 30
BIAS_DEMO_N_LARGE = 3_000
UNBIASED_SHRINK_FLOOR = 7.0
BIASED_FLAT_LOW = 0.4
BIASED_FLAT_HIGH = 2.5

# ---------------------------------------------------------------------------
# Exercise 6 -- the bootstrap, from scratch
# ---------------------------------------------------------------------------

BOOTSTRAP_SAMPLE_SIZE = 200
BOOTSTRAP_SAMPLE_MEAN = 50.0
BOOTSTRAP_SAMPLE_STD = 10.0
BOOTSTRAP_N_BOOT = 5_000
BOOTSTRAP_MEAN_RELATIVE_TOLERANCE = 0.15
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
