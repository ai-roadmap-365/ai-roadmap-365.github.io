"""Exercise 3: simulate a large population and confirm the exact posterior
by counting rather than by formula.

Takes an explicit `numpy.random.Generator`, built by
`numpy.random.default_rng(seed)`, exactly as Day 113's and Day 114's labs
do -- never the legacy `numpy.random.seed` global.
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
    """
    has_condition = rng.random(n) < prevalence
    n_sick = int(has_condition.sum())
    n_well = n - n_sick

    sick_tests_positive = rng.random(n_sick) < sensitivity
    well_tests_negative = rng.random(n_well) < specificity

    true_positive = int(sick_tests_positive.sum())
    false_negative = n_sick - true_positive
    true_negative = int(well_tests_negative.sum())
    false_positive = n_well - true_negative

    return PopulationCounts(
        true_positive=true_positive,
        false_positive=false_positive,
        true_negative=true_negative,
        false_negative=false_negative,
    )
