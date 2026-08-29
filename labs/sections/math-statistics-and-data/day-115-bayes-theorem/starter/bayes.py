"""Exercises 1, 4, 5, 6 and 7: Bayes' theorem, exact, in two equivalent forms.

Fill in the bodies marked `# YOUR CODE HERE`. `dataset.py` has every
constant you need. Every function here returns a `fractions.Fraction`
wherever the answer is rational, so an assertion against it is exact rather
than "close enough" -- the same discipline Day 113's lab used throughout.
"""

from fractions import Fraction


# ---------------------------------------------------------------------------
# Exercise 1: Bayes' theorem in probability form
# ---------------------------------------------------------------------------


def posterior(prior: Fraction, sensitivity: Fraction, specificity: Fraction) -> Fraction:
    """P(condition | positive test), by Bayes' theorem.

    prior        = P(condition), the base rate before any test
    sensitivity  = P(positive | condition)
    specificity  = P(negative | no condition)

    The denominator -- P(positive), the "evidence" -- is exactly Day 113's
    law of total probability applied to the two-piece partition
    {condition, no condition}:

        P(positive) = P(condition) x sensitivity
                    + P(no condition) x (1 - specificity)
    """
    # YOUR CODE HERE
    raise NotImplementedError


def posterior_general(
    prior: Fraction,
    p_positive_given_condition: Fraction,
    p_positive_given_no_condition: Fraction,
) -> Fraction:
    """The same theorem, stated with raw likelihoods instead of sensitivity
    and specificity. Useful whenever "the test is positive" is not a clean
    sensitivity/specificity pair -- for instance, exercise 7's correlated
    tests, where P(both positive | condition) is not simply sensitivity
    squared.
    """
    # YOUR CODE HERE
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 5: the odds form
# ---------------------------------------------------------------------------


def probability_to_odds(p: Fraction) -> Fraction:
    """odds = p / (1 - p)."""
    # YOUR CODE HERE
    raise NotImplementedError


def odds_to_probability(odds: Fraction) -> Fraction:
    """p = odds / (1 + odds), the inverse of probability_to_odds."""
    # YOUR CODE HERE
    raise NotImplementedError


def likelihood_ratio(sensitivity: Fraction, specificity: Fraction) -> Fraction:
    """LR+ = P(positive | condition) / P(positive | no condition)
           = sensitivity / (1 - specificity).
    """
    # YOUR CODE HERE
    raise NotImplementedError


def update_odds(prior_odds: Fraction, ratio: Fraction) -> Fraction:
    """posterior odds = prior odds x likelihood ratio."""
    # YOUR CODE HERE
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 6: sequential updating
# ---------------------------------------------------------------------------


def sequential_posterior(
    prior: Fraction,
    tests: list[tuple[Fraction, Fraction]],
) -> Fraction:
    """Update a prior with a sequence of independent positive test results.

    `tests` is a list of (sensitivity, specificity) pairs. Update the
    running odds one likelihood ratio at a time, then convert back to a
    probability at the end.
    """
    # YOUR CODE HERE
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 7: correlated tests -- when "multiply the likelihood ratios"
# quietly assumes something false
# ---------------------------------------------------------------------------


def independent_pair_probability(single_rate: Fraction) -> Fraction:
    """P(both runs agree on a given outcome | hypothesis), assuming the two
    runs are drawn independently: single_rate squared.
    """
    # YOUR CODE HERE
    raise NotImplementedError


def correlated_pair_probability(single_rate: Fraction, correlation_weight: Fraction) -> Fraction:
    """P(both runs agree on a given outcome | hypothesis), when the two
    runs share a failure mode with probability `correlation_weight`.

    With probability `correlation_weight`, both runs are yoked to one
    shared random draw and therefore either BOTH show the outcome or
    NEITHER does, at the single-run rate. With probability
    (1 - correlation_weight), the two runs are genuinely independent, as
    `independent_pair_probability` assumes for the whole calculation.
    """
    # YOUR CODE HERE
    raise NotImplementedError
