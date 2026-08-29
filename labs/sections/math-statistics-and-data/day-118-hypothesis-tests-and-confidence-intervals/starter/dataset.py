"""Population generators and tolerance constants shared by every exercise.

This file is complete and does not need editing -- your work for each
exercise lives in `inference.py`. Every population here has a KNOWN true
parameter, which is what makes the coverage and duality exercises checkable
at all.
"""
from __future__ import annotations

import numpy as np

POP_MEAN = 50.3
POP_STD = 12.7

POP_B_MEAN = 53.1
POP_B_STD = 12.7

SKEWED_SCALE = 8.0


def normal_population(rng: np.random.Generator, n: int, mean: float, std: float) -> np.ndarray:
    return rng.normal(loc=mean, scale=std, size=n)


def skewed_population(rng: np.random.Generator, n: int, scale: float = SKEWED_SCALE) -> np.ndarray:
    return rng.exponential(scale=scale, size=n)


COVERAGE_TARGET = 0.95
COVERAGE_TRIALS = 10_000
COVERAGE_SAMPLE_N = 300
COVERAGE_SE = (COVERAGE_TARGET * (1 - COVERAGE_TARGET) / COVERAGE_TRIALS) ** 0.5
COVERAGE_TOLERANCE = 3 * COVERAGE_SE

FWER_TRIALS = 20
FWER_ALPHA = 0.05
FWER_EXACT = 1 - (1 - FWER_ALPHA) ** FWER_TRIALS
FWER_FAMILIES = 20_000
FWER_SIM_TOLERANCE = 0.015
BONFERRONI_EXPECTED = 1 - (1 - FWER_ALPHA / FWER_TRIALS) ** FWER_TRIALS
BONFERRONI_TOLERANCE = 0.015

PEEK_ALPHA = 0.05
PEEK_EXPERIMENTS = 4_000
PEEK_BATCH_SIZE = 10
PEEK_MAX_BATCHES = 5
PEEK_MIN_INFLATION_FACTOR = 2.0

BOOTSTRAP_N_BOOT = 5_000
BOOTSTRAP_WIDTH_RATIO_TOLERANCE = 0.20
BOOTSTRAP_CENTER_TOLERANCE_IN_SE = 0.6

POWER_CHECK_EFFECT = 2.8
POWER_CHECK_N = 100
POWER_CHECK_TRIALS = 3_000
POWER_CHECK_TOLERANCE = 0.03

EFFECT_VS_N_RELATIVE_DIFF = 0.005
EFFECT_VS_N_SMALL_N = 30
EFFECT_VS_N_LARGE_N = 100_000
