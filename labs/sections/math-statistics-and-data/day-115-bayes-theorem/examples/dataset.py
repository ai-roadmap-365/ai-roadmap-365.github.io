"""The scenario, the corpus, and every tolerance this lab compares against.

Read this file. Nothing here is tuned to make a test pass: every exact
number is either a stated assumption (a test's sensitivity, a disease's
prevalence) or a value derived from those assumptions and then checked
against enumeration or simulation. The one place a captured figure differs
from the number a naive back-of-envelope calculation might suggest --
exercise 9's log-space arithmetic -- is called out explicitly at the bottom
of this file, because the wrong number belongs nowhere near a test.
"""

import math
from fractions import Fraction

# --------------------------------------------------------------------------
# The opening scenario: a diagnostic test for a rare condition
# --------------------------------------------------------------------------

#: 1 person in 1,000 has the condition, before any test is run.
PREVALENCE: Fraction = Fraction(1, 1000)

#: P(test positive | has condition) -- the test catches 99 sick people out
#: of every 100.
SENSITIVITY: Fraction = Fraction(99, 100)

#: P(test negative | does not have condition) -- the test correctly clears
#: 99 healthy people out of every 100.
SPECIFICITY: Fraction = Fraction(99, 100)

#: The exact posterior, derived by hand in the lesson and reproduced by
#: exercise 1: P(condition | positive) = 99/1098, about 9.02%.
OPENING_POSTERIOR_EXACT: Fraction = Fraction(99, 1098)

assert OPENING_POSTERIOR_EXACT == Fraction(11, 122)
assert round(float(OPENING_POSTERIOR_EXACT), 4) == 0.0902

# --------------------------------------------------------------------------
# The natural-frequencies table: 100,000 people, counted rather than
# multiplied as percentages
# --------------------------------------------------------------------------

NATURAL_FREQUENCY_POPULATION: int = 100_000

#: With prevalence 1/1000, exactly 100 of 100,000 people have the
#: condition, and 99,900 do not -- both exact because the population size
#: was chosen to divide the prevalence evenly.
NATURAL_FREQUENCY_SICK: int = 100
NATURAL_FREQUENCY_WELL: int = 99_900
assert NATURAL_FREQUENCY_SICK + NATURAL_FREQUENCY_WELL == NATURAL_FREQUENCY_POPULATION
assert Fraction(NATURAL_FREQUENCY_SICK, NATURAL_FREQUENCY_POPULATION) == PREVALENCE

#: True positives: 99% of the 100 sick people test positive.
NATURAL_FREQUENCY_TP: int = 99
#: False negatives: the other 1% of the sick people test negative.
NATURAL_FREQUENCY_FN: int = 1
#: False positives: 1% of the 99,900 healthy people test positive anyway.
NATURAL_FREQUENCY_FP: int = 999
#: True negatives: the other 99% of the healthy people correctly test negative.
NATURAL_FREQUENCY_TN: int = 98_901

assert NATURAL_FREQUENCY_TP + NATURAL_FREQUENCY_FN == NATURAL_FREQUENCY_SICK
assert NATURAL_FREQUENCY_FP + NATURAL_FREQUENCY_TN == NATURAL_FREQUENCY_WELL

# --------------------------------------------------------------------------
# Exercise 3: seeded simulation of a large population
# --------------------------------------------------------------------------

SIMULATION_POPULATION: int = 2_000_000
SIMULATION_SEED: int = 42


def standard_error(p: float, n: int) -> float:
    """The standard error of a proportion estimated from n trials."""
    return math.sqrt(p * (1.0 - p) / n)


# --------------------------------------------------------------------------
# Exercise 4: the prevalence sweep
# --------------------------------------------------------------------------

#: A sweep from rare to common, ending at 1/2 -- the prevalence at which
#: the posterior collapses to exactly the sensitivity, 0.99, which is the
#: number almost everyone wrongly gives for the 1-in-1,000 case above.
PREVALENCE_SWEEP: tuple[Fraction, ...] = (
    Fraction(1, 100_000),
    Fraction(1, 10_000),
    Fraction(1, 1_000),
    Fraction(1, 100),
    Fraction(1, 10),
    Fraction(1, 2),
)

# --------------------------------------------------------------------------
# Exercise 6: sequential updating with two DIFFERENT tests
# --------------------------------------------------------------------------

#: Test A is the opening scenario's test: 99% sensitive, 99% specific.
TEST_A_SENSITIVITY: Fraction = SENSITIVITY
TEST_A_SPECIFICITY: Fraction = SPECIFICITY

#: Test B is a different, less accurate test: 95% sensitive, 98% specific.
#: Using two genuinely different tests makes "the order does not matter"
#: a real claim about commutativity rather than a coincidence of running
#: the identical test twice.
TEST_B_SENSITIVITY: Fraction = Fraction(95, 100)
TEST_B_SPECIFICITY: Fraction = Fraction(98, 100)

# --------------------------------------------------------------------------
# Exercise 7: correlated tests -- the same assay, run twice, on one sample
# --------------------------------------------------------------------------

#: The probability that a run shares its outcome with the other run rather
#: than drawing independently -- modelling a shared failure mode, such as
#: a contaminated sample or a single faulty batch of reagent, that affects
#: both runs identically. c = 0 is the naive (fully independent) model;
#: c = 1/2 means half the time both runs are yoked to one shared draw.
CORRELATION_WEIGHT: Fraction = Fraction(1, 2)

#: Both runs use the same underlying test: 99% sensitive, 99% specific.
CORRELATED_SENSITIVITY: Fraction = SENSITIVITY
CORRELATED_SPECIFICITY: Fraction = SPECIFICITY

# --------------------------------------------------------------------------
# Exercise 8: Naive Bayes from scratch -- a tiny hand-made spam corpus
# --------------------------------------------------------------------------

#: Three spam documents, three ham documents. Kept deliberately tiny so the
#: whole vocabulary and every count can be read off by hand and checked.
SPAM_DOCS: tuple[str, ...] = (
    "buy cheap watches now",
    "cheap replica watches for sale",
    "buy now limited offer",
)

HAM_DOCS: tuple[str, ...] = (
    "meeting notes for review",
    "please review the agenda",
    "schedule the project meeting",
)

#: Held-out documents the trained classifier is asked to label.
#:
#: The first two have no word that is entirely absent from one class'
#: training vocabulary, so smoothed and unsmoothed classifiers agree.
#: The third is built to contain exactly one word -- "watches" -- that
#: never appears in the ham training documents, so the unsmoothed
#: classifier's P(document | ham) collapses to exactly zero and the single
#: word vetoes three other words that all point toward ham.
HELD_OUT_CLEAR_SPAM: str = "buy cheap watches"
HELD_OUT_CLEAR_HAM: str = "schedule the project meeting"
HELD_OUT_VETO_CASE: str = "please review schedule watches"

LAPLACE_ALPHA: int = 1

# --------------------------------------------------------------------------
# Exercise 9: why log space is not optional
# --------------------------------------------------------------------------

#: A stand-in for "several hundred small per-word probabilities multiplied
#: together" -- the exact shape of a naive Bayes document score. 500 factors
#: of 0.01 is well inside the range a real bag-of-words likelihood product
#: can reach, and float64 cannot represent the result.
UNDERFLOW_FACTOR: float = 0.01
UNDERFLOW_COUNT: int = 500

#: The true value of the corresponding sum of logs, computed directly
#: rather than approximated: 500 * ln(0.01). This is reported, not assumed
#: -- see the note below.
UNDERFLOW_LOG_SUM: float = UNDERFLOW_COUNT * math.log(UNDERFLOW_FACTOR)

# A note on a figure that does NOT appear as a constant here. An earlier
# draft of this lab's brief stated that 500 factors of 0.01 collapse in log
# space to "about -1151.29". That number is wrong for 500 factors of 0.01 --
# 500 * ln(0.01) = -2302.585..., not -1151.29. The figure -1151.29 is what
# you get from 500 factors of 0.1 (500 * ln(0.1) = -1151.29...), or
# equivalently 250 factors of 0.01. This file and every test in this lab
# use the measured, correct value for 500 factors of 0.01, UNDERFLOW_LOG_SUM
# above, computed directly by math.log rather than copied from a draft.
assert round(UNDERFLOW_LOG_SUM, 2) == -2302.59
