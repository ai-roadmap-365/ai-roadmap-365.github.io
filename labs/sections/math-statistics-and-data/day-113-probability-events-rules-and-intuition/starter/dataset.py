"""The sample space, the events, the urns, and every tolerance this lab
compares against.

Read this file. Nothing here is tuned: every probability below is either
computed by enumeration (via `itertools.product` and `fractions.Fraction`) or
derived algebraically and then checked against the enumeration in the tests.
The simulation tolerance is derived from the standard error of a proportion,
`sqrt(p(1-p)/n)`, with the arithmetic written out beside it -- not chosen by
running a test and loosening the number until it passed.
"""

import itertools
import math
from fractions import Fraction
from typing import Callable

# --------------------------------------------------------------------------
# The sample space: two fair six-sided dice, 36 equally likely outcomes
# --------------------------------------------------------------------------

#: Every ordered pair (first die, second die), each equally likely. Built by
#: enumeration, not written down as a literal list.
TWO_DICE_SPACE: tuple[tuple[int, int], ...] = tuple(
    itertools.product(range(1, 7), range(1, 7))
)

assert len(TWO_DICE_SPACE) == 36

# --------------------------------------------------------------------------
# Events, as predicates over one outcome -- the enumerated set is built by
# filtering the space with these, in probability.py and in the scripts below.
# --------------------------------------------------------------------------


def is_sum(target: int) -> Callable[[tuple[int, int]], bool]:
    """An event predicate: the two dice sum to `target`."""

    def predicate(outcome: tuple[int, int]) -> bool:
        return outcome[0] + outcome[1] == target

    return predicate


def is_first_die(value: int) -> Callable[[tuple[int, int]], bool]:
    """An event predicate: the first die shows `value`."""

    def predicate(outcome: tuple[int, int]) -> bool:
        return outcome[0] == value

    return predicate


def first_die_even(outcome: tuple[int, int]) -> bool:
    """An event predicate: the first die shows an even number."""
    return outcome[0] % 2 == 0


def is_double(outcome: tuple[int, int]) -> bool:
    """An event predicate: both dice show the same value."""
    return outcome[0] == outcome[1]


# --------------------------------------------------------------------------
# The addition rule, on a concrete pair of events
# --------------------------------------------------------------------------

#: A = "the dice sum to 7" (6 outcomes). B = "the first die shows 6" (6
#: outcomes). Their overlap is exactly one outcome, (6, 1), because a first
#: die of 6 needs a second die of 1 to sum to 7. The naive sum P(A) + P(B)
#: double-counts that one outcome, so it overstates P(A union B) by exactly
#: P(A intersect B) = 1/36.
ADDITION_EVENT_A = is_sum(7)
ADDITION_EVENT_B = is_first_die(6)

# --------------------------------------------------------------------------
# The Chevalier de Méré's two bets
# --------------------------------------------------------------------------

#: Bet 1: at least one six in four rolls of one die.
DE_MERE_SINGLE_ROLLS: int = 4
DE_MERE_SINGLE_FACES: int = 6

#: Bet 2: at least one double-six in twenty-four rolls of two dice.
DE_MERE_DOUBLE_ROLLS: int = 24
DE_MERE_DOUBLE_FACES: int = 36  # 6 x 6 possible pairs, one of which is (6, 6)

#: Exact answers, by the complement rule: 1 - P(none of the trials succeed).
#: Fraction keeps every digit; the lesson rounds these to four places.
DE_MERE_SINGLE_EXACT: Fraction = 1 - Fraction(5, 6) ** DE_MERE_SINGLE_ROLLS
DE_MERE_DOUBLE_EXACT: Fraction = 1 - Fraction(35, 36) ** DE_MERE_DOUBLE_ROLLS

assert round(float(DE_MERE_SINGLE_EXACT), 4) == 0.5177
assert round(float(DE_MERE_DOUBLE_EXACT), 4) == 0.4914

# --------------------------------------------------------------------------
# Independence and dependence: two named pairs of events in TWO_DICE_SPACE
# --------------------------------------------------------------------------

#: A genuinely independent pair. "Sum is 7" is independent of "first die is
#: 3" -- for ANY value the first die shows, exactly one value of the second
#: die makes the sum 7, so P(sum = 7 | first die = v) = 1/6 for every v, which
#: is P(sum = 7) itself. That is what independence means.
INDEPENDENT_PAIR = (is_sum(7), is_first_die(3))

#: A genuinely dependent pair. "Sum is 2" requires BOTH dice to show 1, so it
#: is only possible when the first die shows 1 -- P(sum = 2 | first die = 1)
#: = 1/6, but P(sum = 2 | first die != 1) = 0. Those are not equal, so the
#: events are dependent.
DEPENDENT_PAIR = (is_sum(2), is_first_die(1))

# --------------------------------------------------------------------------
# Mutual exclusivity implies dependence
# --------------------------------------------------------------------------

#: "Sum is 2" and "sum is 12" cannot both happen (2 needs (1,1), 12 needs
#: (6,6)), so they are mutually exclusive. Knowing one occurred makes the
#: other impossible -- the sharpest form of dependence there is.
MUTUALLY_EXCLUSIVE_PAIR = (is_sum(2), is_sum(12))

# --------------------------------------------------------------------------
# Conditioning by restriction
# --------------------------------------------------------------------------

#: P(sum = 8 | first die is even), computed two ways in the lab: by the
#: formula P(A and B) / P(B), and by filtering TWO_DICE_SPACE down to the
#: rows where the first die is even and asking what fraction of THOSE rows
#: sum to 8.
CONDITIONING_EVENT_A = is_sum(8)
CONDITIONING_EVENT_B = first_die_even

# --------------------------------------------------------------------------
# The law of total probability: two urns, drawn from with a fair coin
# --------------------------------------------------------------------------

#: Urn 1: 3 red, 7 blue, out of 10 balls.
URN_1_RED: int = 3
URN_1_BLUE: int = 7

#: Urn 2: 6 red, 4 blue, out of 10 balls.
URN_2_RED: int = 6
URN_2_BLUE: int = 4

assert URN_1_RED + URN_1_BLUE == 10
assert URN_2_RED + URN_2_BLUE == 10

#: A fair coin decides which urn to draw from -- P(urn 1) = P(urn 2) = 1/2.
URN_PRIOR: tuple[Fraction, Fraction] = (Fraction(1, 2), Fraction(1, 2))

#: P(red | urn 1) and P(red | urn 2), read straight off each urn's contents.
URN_CONDITIONAL_RED: tuple[Fraction, Fraction] = (
    Fraction(URN_1_RED, URN_1_RED + URN_1_BLUE),
    Fraction(URN_2_RED, URN_2_RED + URN_2_BLUE),
)

# --------------------------------------------------------------------------
# Monte Carlo error scaling
# --------------------------------------------------------------------------

#: The event whose probability the Monte Carlo experiment estimates: two
#: fair dice sum to 7. The exact answer is 1/6, established in exercise 1.
MONTE_CARLO_TARGET: Fraction = Fraction(1, 6)

#: Sample sizes to sweep, four decades apart at the ends.
MONTE_CARLO_SAMPLE_SIZES: tuple[int, ...] = (100, 1_000, 10_000, 100_000)

#: Independent seeds to average over at each sample size, so the assertion is
#: about the SHAPE of the error trend across many runs rather than about one
#: sampled value, which would be flaky on someone else's machine.
MONTE_CARLO_SEEDS: tuple[int, ...] = tuple(range(20))


def standard_error(p: float, n: int) -> float:
    """The standard error of a proportion estimated from n trials.

    This is the quantity that governs how far a Monte Carlo estimate can be
    expected to land from the true probability it estimates: about 68% of
    estimates land within one standard error, and about 99.7% within three.
    """
    return math.sqrt(p * (1.0 - p) / n)


#: Three standard errors, at the sample sizes de Méré's simulations use in
#: exercise 3. This is not a guessed tolerance: it is the width inside which
#: 99.7% of repeated simulations should land, derived from the formula above.
DE_MERE_SIM_TRIALS: int = 200_000
DE_MERE_SINGLE_SE: float = standard_error(float(DE_MERE_SINGLE_EXACT), DE_MERE_SIM_TRIALS)
DE_MERE_DOUBLE_SE: float = standard_error(float(DE_MERE_DOUBLE_EXACT), DE_MERE_SIM_TRIALS)
DE_MERE_SINGLE_TOL: float = 3.0 * DE_MERE_SINGLE_SE
DE_MERE_DOUBLE_TOL: float = 3.0 * DE_MERE_DOUBLE_SE

# --------------------------------------------------------------------------
# Reproducibility
# --------------------------------------------------------------------------

REPRODUCIBILITY_SEED_A: int = 42
REPRODUCIBILITY_SEED_B: int = 43
REPRODUCIBILITY_TRIALS: int = 10_000
