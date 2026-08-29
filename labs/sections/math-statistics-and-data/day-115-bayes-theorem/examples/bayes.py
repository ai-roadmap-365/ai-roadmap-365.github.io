"""Exercises 1, 4, 5, 6 and 7: Bayes' theorem, exact, in two equivalent forms.

Every function here returns a `fractions.Fraction` wherever the answer is
rational, so an assertion against it is exact rather than "close enough" --
the same discipline Day 113's lab used throughout.
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
    p_condition_and_positive = prior * sensitivity
    p_no_condition_and_positive = (1 - prior) * (1 - specificity)
    evidence = p_condition_and_positive + p_no_condition_and_positive
    return p_condition_and_positive / evidence


def posterior_general(
    prior: Fraction,
    p_positive_given_condition: Fraction,
    p_positive_given_no_condition: Fraction,
) -> Fraction:
    """The same theorem, stated with raw likelihoods instead of sensitivity
    and specificity.

    Useful whenever "the test is positive" is not a clean sensitivity/
    specificity pair -- for instance, exercise 7's correlated tests, where
    P(both positive | condition) is not simply sensitivity squared.
    """
    numerator = prior * p_positive_given_condition
    evidence = numerator + (1 - prior) * p_positive_given_no_condition
    return numerator / evidence


# ---------------------------------------------------------------------------
# Exercise 5: the odds form
# ---------------------------------------------------------------------------


def probability_to_odds(p: Fraction) -> Fraction:
    """odds = p / (1 - p)."""
    return p / (1 - p)


def odds_to_probability(odds: Fraction) -> Fraction:
    """p = odds / (1 + odds), the inverse of probability_to_odds."""
    return odds / (1 + odds)


def likelihood_ratio(sensitivity: Fraction, specificity: Fraction) -> Fraction:
    """LR+ = P(positive | condition) / P(positive | no condition)
           = sensitivity / (1 - specificity).

    The likelihood ratio isolates how much a positive result is worth on
    its own, independent of whatever you believed going in -- multiply it
    onto the prior odds and you get the posterior odds directly.
    """
    return sensitivity / (1 - specificity)


def update_odds(prior_odds: Fraction, ratio: Fraction) -> Fraction:
    """posterior odds = prior odds x likelihood ratio."""
    return prior_odds * ratio


# ---------------------------------------------------------------------------
# Exercise 6: sequential updating
# ---------------------------------------------------------------------------


def sequential_posterior(
    prior: Fraction,
    tests: list[tuple[Fraction, Fraction]],
) -> Fraction:
    """Update a prior with a sequence of independent positive test results.

    `tests` is a list of (sensitivity, specificity) pairs, applied one
    likelihood ratio at a time in odds form. Because Fraction
    multiplication is commutative, the final odds -- and therefore the
    final posterior -- do not depend on the order `tests` is given in;
    that is asserted directly in the reference test suite, not just
    claimed here.
    """
    odds = probability_to_odds(prior)
    for sensitivity, specificity in tests:
        odds = update_odds(odds, likelihood_ratio(sensitivity, specificity))
    return odds_to_probability(odds)


# ---------------------------------------------------------------------------
# Exercise 7: correlated tests -- when "multiply the likelihood ratios"
# quietly assumes something false
# ---------------------------------------------------------------------------


def independent_pair_probability(single_rate: Fraction) -> Fraction:
    """P(both runs agree on a given outcome | hypothesis), assuming the two
    runs are drawn independently: single_rate squared.

    This is what "multiply the likelihood ratios twice" is implicitly
    assuming. It is correct when the two test runs really are conditionally
    independent given the hypothesis, and silently wrong when they are not.
    """
    return single_rate**2


def correlated_pair_probability(single_rate: Fraction, correlation_weight: Fraction) -> Fraction:
    """P(both runs agree on a given outcome | hypothesis), when the two
    runs share a failure mode with probability `correlation_weight`.

    With probability `correlation_weight`, both runs are yoked to one
    shared random draw (a contaminated sample, a single bad reagent batch)
    and therefore either BOTH show the outcome or NEITHER does, at the
    single-run rate. With probability (1 - correlation_weight), the two
    runs are genuinely independent, as `independent_pair_probability`
    assumes for the whole calculation.
    """
    shared = correlation_weight * single_rate
    independent = (1 - correlation_weight) * independent_pair_probability(single_rate)
    return shared + independent
