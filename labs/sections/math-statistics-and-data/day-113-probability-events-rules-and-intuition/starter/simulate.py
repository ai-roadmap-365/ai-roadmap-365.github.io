"""Exercise 3, 8 and 9: simulation, and the error that comes with it.

Every simulation here takes an explicit `numpy.random.Generator` -- built by
`numpy.random.default_rng(seed)` -- rather than touching global random state.
Two calls with the same seed must return byte-identical arrays; that is
`default_rng`'s whole advantage over the legacy `numpy.random.seed` global,
and exercise 9 asserts it directly.
"""

import numpy as np


# ---------------------------------------------------------------------------
# Exercise 3: de Méré's two bets, simulated
# ---------------------------------------------------------------------------


def simulate_at_least_one_six(rng: np.random.Generator, trials: int) -> float:
    """Simulate de Méré's first bet: at least one 6 in 4 rolls of one die.

    Roll a (trials, 4) array of dice, and return the fraction of rows that
    contain at least one 6. Vectorised: no Python-level loop over trials.
    """
    # YOUR CODE HERE
    raise NotImplementedError


def simulate_at_least_one_double_six(rng: np.random.Generator, trials: int) -> float:
    """Simulate de Méré's second bet: at least one double-six in 24 rolls of
    two dice.

    Roll two (trials, 24) arrays -- one per die -- and return the fraction of
    rows in which some roll shows 6 on both dice at once.
    """
    # YOUR CODE HERE
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 8: Monte Carlo error scaling
# ---------------------------------------------------------------------------


def simulate_sum_seven(rng: np.random.Generator, trials: int) -> float:
    """Simulate P(two fair dice sum to 7) by rolling `trials` pairs of dice.

    Returns the fraction of pairs that summed to 7. The exact answer,
    established in exercise 1, is exactly 1/6.
    """
    # YOUR CODE HERE
    raise NotImplementedError
