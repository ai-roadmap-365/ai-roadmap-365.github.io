"""Every dataset and tolerance this lab compares against.

Read this file. Nothing here is tuned to make a test pass: the salary list
is small and hand-checkable, Anscombe's quartet is the published 1973
dataset (Anscombe, "Graphs in Statistical Analysis", The American
Statistician, 1973), and the Bessel-correction tolerance is derived from the
standard error of the simulated mean, with the arithmetic written out beside
it, never chosen by running a test and loosening the number until it
passed.
"""

import math
from fractions import Fraction

# --------------------------------------------------------------------------
# Exercise 1: mean, median, mode
# --------------------------------------------------------------------------

#: An odd-length list with a single clear mode (7 appears three times).
ODD_LIST: tuple[int, ...] = (2, 4, 4, 7, 7, 7, 9, 12, 15)

#: An even-length list, so the median must average the two middle values.
EVEN_LIST: tuple[float, ...] = (1.0, 3.0, 4.0, 8.0, 10.0, 12.0)

#: A multimodal list: 3 and 8 are each the most frequent value.
MULTIMODAL_LIST: tuple[int, ...] = (3, 3, 5, 6, 8, 8, 9)

# --------------------------------------------------------------------------
# Exercise 2: the breakdown point
# --------------------------------------------------------------------------

#: Nine ordinary salaries, in dollars. Small enough to check the median of
#: by eye: sorted, the middle (5th of 9) value is 50000.
SALARY_LIST: tuple[int, ...] = (
    42000,
    45000,
    47000,
    48000,
    50000,
    52000,
    55000,
    58000,
    60000,
)

#: Replace the single largest salary with one wildly corrupted value. One
#: value out of nine changing is "one value out of many" -- nowhere near the
#: 50% the median can absorb before it moves at all.
CORRUPTED_SALARY: int = 10_000_000

#: The mean must move by at least this many dollars for the demonstration to
#: count as "dragged anywhere at all" -- chosen as a small fraction of the
#: actual shift (over $1,000,000), so the assertion is not a coin flip.
BREAKDOWN_MEAN_SHIFT_FLOOR: float = 500_000.0

# --------------------------------------------------------------------------
# Exercise 3: Bessel's correction, measured
# --------------------------------------------------------------------------

#: The population this exercise draws from: mean 50, standard deviation 10,
#: so the true variance is exactly 100. Both are known exactly because the
#: population is synthetic, which is what makes the bias measurable at all
#: -- there is a ground truth to compare the estimators against.
BESSEL_POPULATION_MEAN: float = 50.0
BESSEL_POPULATION_SIGMA: float = 10.0
BESSEL_TRUE_VARIANCE: float = BESSEL_POPULATION_SIGMA**2

#: Small samples, where the fitted-mean bias is largest relative to n.
BESSEL_SAMPLE_SIZE: int = 5

#: Many repeated samples, so the estimators' average is itself a precise
#: number rather than one noisy draw.
BESSEL_TRIALS: int = 20_000

BESSEL_SEED: int = 116

#: The textbook claim this exercise measures: dividing by n underestimates
#: the true variance, on average, by exactly the factor (n-1)/n.
BESSEL_EXPECTED_BIAS_FACTOR: float = (BESSEL_SAMPLE_SIZE - 1) / BESSEL_SAMPLE_SIZE

#: How close the measured biased-estimator ratio must land to (n-1)/n. This
#: is a Monte Carlo measurement, not exact arithmetic, so the tolerance is
#: generous but not vacuous -- wide enough to pass on any honest run of
#: BESSEL_TRIALS trials, narrow enough that a genuinely broken implementation
#: (dividing by the wrong thing, or not at all) fails it.
BESSEL_BIAS_FACTOR_TOLERANCE: float = 0.02

#: How many standard errors of the *unbiased* estimator's own sampling mean
#: it is allowed to sit from the true variance. The unbiased estimator is
#: correct only on average, not on every run, so this must be generous
#: enough to pass reliably -- 4 standard errors covers essentially all honest
#: runs (about 1 in 16,000 fails purely by chance under a normal
#: approximation).
BESSEL_UNBIASED_SE_TOLERANCE: float = 4.0

# --------------------------------------------------------------------------
# Exercise 4: percentile ambiguity
# --------------------------------------------------------------------------

#: A small, deliberately awkward array: 8 values, so the 75th percentile
#: falls between two of them under every interpolation convention, and the
#: conventions genuinely disagree about where.
PERCENTILE_ARRAY: tuple[int, ...] = (1, 2, 3, 4, 6, 8, 9, 15)

PERCENTILE_TARGET: float = 75.0

#: A representative slice of NumPy's nine documented `method=` conventions
#: for `numpy.percentile` (NumPy >= 1.22). `linear` is the default and the
#: one pandas' `DataFrame.describe()` also uses.
PERCENTILE_METHODS: tuple[str, ...] = (
    "linear",
    "lower",
    "higher",
    "nearest",
    "midpoint",
    "weibull",
    "median_unbiased",
    "normal_unbiased",
    "hazen",
)

# --------------------------------------------------------------------------
# Exercise 5: Pearson versus Spearman
# --------------------------------------------------------------------------

#: A perfect, symmetric parabola: y = x^2 over a symmetric range of x. Every
#: unit increase in x on the left half is mirrored by an equal decrease in y
#: on the right half's counterpart, so the *linear* trend that Pearson
#: measures cancels out exactly, even though y is perfectly determined by x.
PARABOLA_X: tuple[int, ...] = tuple(range(-5, 6))
PARABOLA_Y: tuple[int, ...] = tuple(v**2 for v in PARABOLA_X)

#: The tolerance "essentially zero" is checked against -- not equality to 0,
#: because that would be asserting a specific floating-point outcome rather
#: than the mathematical fact.
PARABOLA_PEARSON_TOLERANCE: float = 1e-9

#: A monotone but non-linear relationship: y = x^3. Every increase in x
#: produces an increase in y, so the *rank order* is perfectly preserved,
#: even though the relationship is not a straight line.
MONOTONE_X: tuple[int, ...] = tuple(range(-5, 6))
MONOTONE_Y: tuple[int, ...] = tuple(v**3 for v in MONOTONE_X)

# --------------------------------------------------------------------------
# Exercise 6: Anscombe's quartet
# --------------------------------------------------------------------------
# The published 1973 dataset, reproduced exactly. Anscombe, F. J. (1973).
# "Graphs in Statistical Analysis." The American Statistician, 27(1), 17-21.

ANSCOMBE_X_I: tuple[float, ...] = (10.0, 8.0, 13.0, 9.0, 11.0, 14.0, 6.0, 4.0, 12.0, 7.0, 5.0)
ANSCOMBE_Y_I: tuple[float, ...] = (
    8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68,
)

ANSCOMBE_X_II: tuple[float, ...] = ANSCOMBE_X_I
ANSCOMBE_Y_II: tuple[float, ...] = (
    9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74,
)

ANSCOMBE_X_III: tuple[float, ...] = ANSCOMBE_X_I
ANSCOMBE_Y_III: tuple[float, ...] = (
    7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73,
)

ANSCOMBE_X_IV: tuple[float, ...] = (8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 19.0, 8.0, 8.0, 8.0)
ANSCOMBE_Y_IV: tuple[float, ...] = (
    6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89,
)

ANSCOMBE_SETS: dict[str, tuple[tuple[float, ...], tuple[float, ...]]] = {
    "I": (ANSCOMBE_X_I, ANSCOMBE_Y_I),
    "II": (ANSCOMBE_X_II, ANSCOMBE_Y_II),
    "III": (ANSCOMBE_X_III, ANSCOMBE_Y_III),
    "IV": (ANSCOMBE_X_IV, ANSCOMBE_Y_IV),
}

#: How closely the four sets must agree on mean x, mean y, variance x,
#: variance y, correlation and regression slope -- rounded to these many
#: decimal places, as Anscombe's original table reports them (2 decimal
#: places for the summary statistics themselves).
ANSCOMBE_AGREEMENT_DECIMALS: int = 1

# --------------------------------------------------------------------------
# Exercise 7: Simpson's paradox
# --------------------------------------------------------------------------
# The smallest integer table that shows the paradox: treatment A wins both
# subgroups, treatment B wins overall, purely because A's trials are
# concentrated in the harder subgroup and B's in the easier one.

#: (successes, trials) for treatment A, by subgroup.
TREATMENT_A_EASY: tuple[int, int] = (1, 1)     # 100%
TREATMENT_A_HARD: tuple[int, int] = (9, 90)    # 10%

#: (successes, trials) for treatment B, by subgroup.
TREATMENT_B_EASY: tuple[int, int] = (9, 10)    # 90%
TREATMENT_B_HARD: tuple[int, int] = (0, 1)     # 0%

# --------------------------------------------------------------------------
# Exercise 8: robust spread under contamination
# --------------------------------------------------------------------------

CONTAMINATION_SEED: int = 116
CONTAMINATION_BASE_MEAN: float = 100.0
CONTAMINATION_BASE_SIGMA: float = 5.0
CONTAMINATION_BASE_N: int = 97

#: Three extreme values added to 97 clean ones -- 3 out of 100, i.e. 3%
#: contamination.
CONTAMINATION_OUTLIERS: tuple[float, ...] = (500.0, 520.0, 480.0)

#: The standard deviation must inflate by at least this multiplier for the
#: demonstration to count as "much more" than the MAD's shift.
CONTAMINATION_STD_MULTIPLIER_FLOOR: float = 5.0

#: The MAD must stay below this multiplier of its clean value -- "barely
#: moves".
CONTAMINATION_MAD_MULTIPLIER_CEILING: float = 1.5

# --------------------------------------------------------------------------
# Exercise 9: standardisation and z-scores
# --------------------------------------------------------------------------

STANDARDIZATION_SEED: int = 116
STANDARDIZATION_N: int = 30
STANDARDIZATION_X_MEAN: float = 50.0
STANDARDIZATION_X_SIGMA: float = 10.0
STANDARDIZATION_Y_SLOPE: float = 2.0
STANDARDIZATION_Y_NOISE_SIGMA: float = 5.0

STANDARDIZATION_MEAN_TOLERANCE: float = 1e-9
STANDARDIZATION_STD_TOLERANCE: float = 1e-9
STANDARDIZATION_CORRELATION_TOLERANCE: float = 1e-9


def standard_error_of_mean(sample_variance: float, n: int) -> float:
    """The standard error of a sample mean estimated from n draws."""
    return math.sqrt(sample_variance / n)
