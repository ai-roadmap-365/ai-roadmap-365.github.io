"""Exercises 1 through 10 -- eighteen predictions.

Replace each `None` with the value you think is correct. A `None` is a
skip, not a failure: `pytest starter -q` counts only what you have
attempted. When you are wrong it prints both your answer and the real one,
so a wrong guess is worth more than a blank.

Predict BEFORE you run anything. The two that catch almost everyone are the
seven-to-two ratio (exercise 1) and whether Var[X+Y] equals the naive sum
(exercise 5) -- and they only catch you if you commit first.

Every answer is a number or a Python bool.
"""

ANSWERS: dict[str, object] = {
    # ----------------------------------------------------------------------
    # Exercise 1 -- the pmf of a sum
    # ----------------------------------------------------------------------
    # 1.1 P(the two dice sum to 7), as a decimal.
    "p_sum_seven": None,
    # 1.2 How many times as likely is a sum of 7 as a sum of 2?
    "ratio_seven_to_two": None,
    # ----------------------------------------------------------------------
    # Exercise 2 -- the cdf
    # ----------------------------------------------------------------------
    # 2.1 F(12), the cdf at its largest value.
    "cdf_at_twelve": None,
    # 2.2 F(7) - F(6), as a decimal.
    "cdf_difference_seven_six": None,
    # ----------------------------------------------------------------------
    # Exercise 3 -- expectation and variance
    # ----------------------------------------------------------------------
    # 3.1 E[Y], the expected sum of two dice.
    "expectation_of_sum": None,
    # 3.2 Var[Y], as a decimal.
    "variance_of_sum": None,
    # ----------------------------------------------------------------------
    # Exercise 4 -- linearity with a dependent pair
    # ----------------------------------------------------------------------
    # 4.1 E[X + Y] where X = first die, Y = sum of both dice.
    "expectation_x_plus_y": None,
    # 4.2 Does E[X + Y] == E[X] + E[Y] hold even though X and Y are
    #     dependent?
    "linearity_holds_for_dependent_pair": None,
    # ----------------------------------------------------------------------
    # Exercise 5 -- variance is not additive
    # ----------------------------------------------------------------------
    # 5.1 Does Var[X + Y] == Var[X] + Var[Y] (the naive, WRONG sum)?
    "variance_naive_sum_holds": None,
    # 5.2 Var[X + Y], as a decimal.
    "variance_x_plus_y": None,
    # ----------------------------------------------------------------------
    # Exercise 6 -- Jensen's inequality
    # ----------------------------------------------------------------------
    # 6.1 Is E[X^2] strictly greater than (E[X])^2 for a single die?
    "jensen_strict_for_die": None,
    # 6.2 Does the gap E[X^2] - (E[X])^2 equal Var[X] exactly?
    "jensen_gap_equals_variance": None,
    # ----------------------------------------------------------------------
    # Exercise 7 -- inverse-CDF discrete sampling
    # ----------------------------------------------------------------------
    # 7.1 Does the same seed reproduce identical draws?
    "discrete_sampler_reproducible": None,
    # ----------------------------------------------------------------------
    # Exercise 8 -- exponential from scratch
    # ----------------------------------------------------------------------
    # 8.1 Are all draws from the from-scratch exponential sampler
    #     non-negative?
    "exponential_scratch_nonnegative": None,
    # ----------------------------------------------------------------------
    # Exercise 9 -- Poisson as a Binomial limit
    # ----------------------------------------------------------------------
    # 9.1 Does the maximum pmf gap decrease monotonically as n grows across
    #     10, 100, 1000, 10000?
    "poisson_gap_decreases_monotonically": None,
    # ----------------------------------------------------------------------
    # Exercise 10 -- density above 1
    # ----------------------------------------------------------------------
    # 10.1 The density of Uniform(0, 0.5) at any point in its support.
    "uniform_density_value": None,
    # 10.2 Is that density value greater than 1?
    "uniform_density_exceeds_one": None,
    # 10.3 Does the numeric integral of that density over its support equal
    #      1 (to a small tolerance)?
    "uniform_integral_equals_one": None,
}
