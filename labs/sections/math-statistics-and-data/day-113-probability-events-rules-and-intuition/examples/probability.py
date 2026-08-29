"""Exercise 1, 2, 4, 5, 6 and 7: exact probability, computed two ways.

Every function here returns a `fractions.Fraction` wherever the answer is
rational, so an assertion against it is exact rather than "close enough".
"""

import itertools
from fractions import Fraction
from typing import Callable, Iterable


# ---------------------------------------------------------------------------
# Exercise 1: the sample space, and probability as counting
# ---------------------------------------------------------------------------


def sample_space_two_dice() -> tuple[tuple[int, int], ...]:
    """Every ordered pair (first die, second die), 36 outcomes."""
    return tuple(itertools.product(range(1, 7), range(1, 7)))


def event(
    space: Iterable[tuple[int, int]], predicate: Callable[[tuple[int, int]], bool]
) -> frozenset[tuple[int, int]]:
    """The subset of `space` for which `predicate` is true."""
    return frozenset(outcome for outcome in space if predicate(outcome))


def probability(
    outcome_set: Iterable[tuple[int, int]], space: Iterable[tuple[int, int]]
) -> Fraction:
    """P(event), for equally likely outcomes: |event| / |space|, exactly."""
    outcome_set = frozenset(outcome_set)
    space = tuple(space)
    return Fraction(len(outcome_set), len(space))


# ---------------------------------------------------------------------------
# Exercise 2: the addition rule
# ---------------------------------------------------------------------------


def addition_rule(p_a: Fraction, p_b: Fraction, p_a_and_b: Fraction) -> Fraction:
    """P(A or B) = P(A) + P(B) - P(A and B)."""
    return p_a + p_b - p_a_and_b


def naive_sum(p_a: Fraction, p_b: Fraction) -> Fraction:
    """The wrong shortcut: P(A) + P(B), which double-counts the overlap."""
    return p_a + p_b


# ---------------------------------------------------------------------------
# Exercise 3 helper: the complement rule
# ---------------------------------------------------------------------------


def complement(p: Fraction) -> Fraction:
    """P(not A) = 1 - P(A)."""
    return 1 - p


def at_least_one(p_single_success: Fraction, trials: int) -> Fraction:
    """P(at least one success in `trials` independent tries).

    Collapsed to one line with the complement rule: 1 minus the probability
    that every single trial fails.
    """
    p_single_failure = complement(p_single_success)
    return complement(p_single_failure**trials)


# ---------------------------------------------------------------------------
# Exercise 4: independence
# ---------------------------------------------------------------------------


def is_independent(p_a: Fraction, p_b: Fraction, p_a_and_b: Fraction) -> bool:
    """True exactly when P(A and B) == P(A) * P(B)."""
    return p_a_and_b == p_a * p_b


# ---------------------------------------------------------------------------
# Exercise 5 and 6: conditional probability
# ---------------------------------------------------------------------------


def conditional(p_a_and_b: Fraction, p_b: Fraction) -> Fraction:
    """P(A | B) = P(A and B) / P(B)."""
    if p_b == 0:
        raise ValueError("conditional probability given a zero-probability event")
    return p_a_and_b / p_b


# ---------------------------------------------------------------------------
# Exercise 7: the law of total probability
# ---------------------------------------------------------------------------


def total_probability(
    priors: Iterable[Fraction], conditionals: Iterable[Fraction]
) -> Fraction:
    """P(A) = sum over i of P(A | condition_i) * P(condition_i)."""
    total = Fraction(0)
    for prior, cond in zip(priors, conditionals):
        total += prior * cond
    return total
