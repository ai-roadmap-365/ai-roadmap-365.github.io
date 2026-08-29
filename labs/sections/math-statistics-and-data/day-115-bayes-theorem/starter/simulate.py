"""Exercise 3: simulate a large population and confirm the exact posterior
by counting rather than by formula.

Takes an explicit `numpy.random.Generator`, built by
`numpy.random.default_rng(seed)`, exactly as Day 113's and Day 114's labs
do -- never the legacy `numpy.random.seed` global. Fill in the body marked
`# YOUR CODE HERE`.
"""

from typing import NamedTuple

import numpy as np


class PopulationCounts(NamedTuple):
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int

    @property
    def positives(self) -> int:
        return self.true_positive + self.false_positive

    @property
    def empirical_posterior(self) -> float:
        """TP / (TP + FP) -- the fraction of positive results that are
        genuinely true positives, read straight off the simulated counts."""
        if self.positives == 0:
            return float("nan")
        return self.true_positive / self.positives


def simulate_population(
    rng: np.random.Generator,
    n: int,
    prevalence: float,
    sensitivity: float,
    specificity: float,
) -> PopulationCounts:
    """Draw n people, assign each a true condition status by `prevalence`,
    then a test result by `sensitivity`/`specificity`, and count the four
    outcome cells directly -- no formula involved anywhere in this function.

    Hints:
      - `rng.random(n) < prevalence` gives a boolean array of who has the
        condition.
      - Split the population into sick and well groups, draw test results
        for each group separately with `rng.random(count) < rate`, and
        count how many land on each side.
    """
    # YOUR CODE HERE
    raise NotImplementedError
