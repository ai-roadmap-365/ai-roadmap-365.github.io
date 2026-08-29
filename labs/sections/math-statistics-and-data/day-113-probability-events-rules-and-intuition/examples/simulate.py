"""Exercise 3, 8 and 9: simulation, and the error that comes with it.

Every simulation here takes an explicit `numpy.random.Generator` -- built by
`numpy.random.default_rng(seed)` -- rather than touching global random state.
Two calls with the same seed return byte-identical arrays; that is
`default_rng`'s whole advantage over the legacy `numpy.random.seed` global,
and exercise 9 asserts it directly.
"""

import numpy as np


# ---------------------------------------------------------------------------
# Exercise 3: de Méré's two bets, simulated
# ---------------------------------------------------------------------------


def simulate_at_least_one_six(rng: np.random.Generator, trials: int) -> float:
    """Simulate de Méré's first bet: at least one 6 in 4 rolls of one die."""
    rolls = rng.integers(1, 7, size=(trials, 4))
    at_least_one = (rolls == 6).any(axis=1)
    return float(np.mean(at_least_one))


def simulate_at_least_one_double_six(rng: np.random.Generator, trials: int) -> float:
    """Simulate de Méré's second bet: at least one double-six in 24 rolls of
    two dice."""
    first = rng.integers(1, 7, size=(trials, 24))
    second = rng.integers(1, 7, size=(trials, 24))
    double_six = (first == 6) & (second == 6)
    at_least_one = double_six.any(axis=1)
    return float(np.mean(at_least_one))


# ---------------------------------------------------------------------------
# Exercise 8: Monte Carlo error scaling
# ---------------------------------------------------------------------------


def simulate_sum_seven(rng: np.random.Generator, trials: int) -> float:
    """Simulate P(two fair dice sum to 7) by rolling `trials` pairs of dice."""
    first = rng.integers(1, 7, size=trials)
    second = rng.integers(1, 7, size=trials)
    return float(np.mean(first + second == 7))
