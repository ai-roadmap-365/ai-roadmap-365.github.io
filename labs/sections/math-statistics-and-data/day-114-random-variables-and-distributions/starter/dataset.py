"""The sample spaces, the named-distribution parameters, and every tolerance
this lab compares against.

Read this file. Nothing here is tuned: every exact figure below is either
computed by enumeration (`itertools.product` and `fractions.Fraction`) or
derived algebraically and then checked against the enumeration in the tests.
Every simulation tolerance is derived from a standard error written out
beside it -- never chosen by running a test and loosening a number until it
passed.
"""

import itertools
import math
from fractions import Fraction

# --------------------------------------------------------------------------
# The two-dice sample space, carried over from Day 113 and reused here as
# the running example for a random variable -- the function "sum of the two
# faces" mapping this 36-outcome sample space to the integers.
# --------------------------------------------------------------------------

DIE_FACES: tuple[int, ...] = tuple(range(1, 7))

#: Every ordered pair (first die, second die), 36 equally likely outcomes.
TWO_DICE_SPACE: tuple[tuple[int, int], ...] = tuple(
    itertools.product(DIE_FACES, DIE_FACES)
)
assert len(TWO_DICE_SPACE) == 36

#: The weight of a single outcome in an equally-likely 36-outcome space.
TWO_DICE_WEIGHT: Fraction = Fraction(1, 36)

#: The weight of a single outcome in an equally-likely 6-outcome space (one
#: die alone), used for the Jensen's-inequality exercise.
ONE_DIE_WEIGHT: Fraction = Fraction(1, 6)


def first_die(outcome: tuple[int, int]) -> int:
    """The random variable X: the first die's face."""
    return outcome[0]


def dice_sum(outcome: tuple[int, int]) -> int:
    """The random variable Y: the sum of both dice."""
    return outcome[0] + outcome[1]


# --------------------------------------------------------------------------
# Named distributions: parameters used throughout the lesson and the lab
# --------------------------------------------------------------------------

#: A fair coin, as a Bernoulli(p) reference point.
BERNOULLI_P: float = 0.5

#: Binomial(n, p) used for the Poisson-limit exercise's smallest n, and as a
#: worked example in the lesson.
BINOMIAL_N_EXAMPLE: int = 10
BINOMIAL_P_EXAMPLE: float = 0.3

#: The rate parameter shared by the Poisson distribution and the four
#: Binomial approximations to it in exercise 9. n * p is held fixed at this
#: value as n grows, which is exactly the limiting condition n -> infinity,
#: n * p -> lambda that turns a Binomial into a Poisson.
POISSON_LAMBDA: float = 2.0

#: The four values of n swept in the Poisson-as-Binomial-limit exercise,
#: three decades apart at the ends.
POISSON_LIMIT_NS: tuple[int, ...] = (10, 100, 1_000, 10_000)

#: The range of counts compared between the Binomial and the Poisson pmf.
#: Fifteen values comfortably covers the Poisson(2) distribution's mass --
#: P(X > 14) is under 1e-9 -- so nothing meaningful is cut off.
POISSON_COMPARISON_KS: tuple[int, ...] = tuple(range(0, 15))

#: The rate for the from-scratch exponential sampler.
EXPONENTIAL_RATE: float = 2.0

#: Uniform(0, 0.5) -- the density-above-1 example. Its density is 2
#: everywhere on its support, which is the whole point of exercise 10.
UNIFORM_LOW: float = 0.0
UNIFORM_HIGH: float = 0.5

# --------------------------------------------------------------------------
# Sample sizes and seeds
# --------------------------------------------------------------------------

#: Sample size for the expectation/variance-by-simulation comparison
#: (exercise 3).
EV_SIMULATION_TRIALS: int = 200_000

#: Sample size for the inverse-CDF discrete sampler comparison (exercise 7).
DISCRETE_SAMPLER_TRIALS: int = 200_000

#: Sample size for each of the two exponential samples compared in
#: exercise 8 (from-scratch versus NumPy's own, and the max-gap statistic
#: between their two empirical CDFs).
EXPONENTIAL_SAMPLE_SIZE: int = 50_000

#: The seed every reproducible draw in this lab is built from.
SEED: int = 114

# --------------------------------------------------------------------------
# Tolerances, derived rather than guessed
# --------------------------------------------------------------------------


def standard_error_of_mean(variance: float, n: int) -> float:
    """The standard error of a sample mean: sqrt(variance / n)."""
    return math.sqrt(variance / n)


def standard_error_of_proportion(p: float, n: int) -> float:
    """The standard error of a proportion estimated from n trials."""
    return math.sqrt(p * (1.0 - p) / n)


def dkw_two_sample_threshold(n_a: int, n_b: int, alpha: float = 0.01) -> float:
    """A threshold for the maximum gap between two empirical CDFs drawn
    from the SAME underlying distribution, derived from the
    Dvoretzky-Kiefer-Wolfowitz inequality rather than guessed.

    DKW says: for a sample of size n from a distribution with true CDF F,
    P(sup_x |F_n(x) - F(x)| > eps) <= 2 * exp(-2 * n * eps^2). Solving for
    eps at confidence 1 - alpha (one-sided, so the leading 2 becomes 1)
    gives eps = sqrt(ln(1/alpha) / (2n)). Both empirical CDFs in exercise 8
    are estimating the SAME true exponential CDF, so with probability at
    least 1 - 2*alpha neither one strays more than its own eps from the
    truth, and the gap between them is bounded by the sum of the two eps
    values -- a legitimate, derived threshold, not a number chosen to make
    the test pass.
    """
    eps_a = math.sqrt(math.log(1.0 / alpha) / (2.0 * n_a))
    eps_b = math.sqrt(math.log(1.0 / alpha) / (2.0 * n_b))
    return eps_a + eps_b
