"""Exercises 1 through 9 -- seventeen predictions.

Replace each `None` with the value you think is correct. A `None` is a skip,
not a failure: `pytest starter -q` counts only what you have attempted. When
you are wrong it prints both your answer and the real one, so a wrong guess
is worth more than a blank.

Predict BEFORE you run anything. The two that catch almost everyone are the
breakdown-point question (exercise 2) and the percentile-agreement question
(exercise 4) -- and they only catch you if you commit to a guess first.

Every answer is a number or a Python bool.
"""

ANSWERS: dict[str, object] = {
    # ----------------------------------------------------------------------
    # Exercise 1 -- mean, median, mode
    # ----------------------------------------------------------------------
    # 1.1 The mean of (2, 4, 4, 7, 7, 7, 9, 12, 15), as a decimal.
    "odd_list_mean": None,
    # 1.2 The median of (1.0, 3.0, 4.0, 8.0, 10.0, 12.0) -- an even-length
    #     list, so this is an average of two values.
    "even_list_median": None,
    # ----------------------------------------------------------------------
    # Exercise 2 -- the breakdown point
    # ----------------------------------------------------------------------
    # 2.1 Replace the salary list's largest value ($60,000) with
    #     $10,000,000. Does the MEAN move by more than $500,000?
    "mean_breaks_down": None,
    # 2.2 Under the same corruption, does the MEDIAN move at all
    #     (True/False)?
    "median_breaks_down": None,
    # ----------------------------------------------------------------------
    # Exercise 3 -- Bessel's correction
    # ----------------------------------------------------------------------
    # 3.1 Divide by n instead of n-1: is the resulting variance estimate
    #     biased HIGH, LOW, or unbiased? Answer "high", "low", or
    #     "unbiased".
    "divide_by_n_bias_direction": None,
    # ----------------------------------------------------------------------
    # Exercise 4 -- percentile ambiguity
    # ----------------------------------------------------------------------
    # 4.1 Across NumPy's nine `method=` conventions, do at least two of them
    #     disagree on the 75th percentile of (1, 2, 3, 4, 6, 8, 9, 15)?
    "percentile_methods_disagree": None,
    # 4.2 The default ('linear') method's answer, as a decimal.
    "percentile_linear_value": None,
    # ----------------------------------------------------------------------
    # Exercise 5 -- Pearson versus Spearman
    # ----------------------------------------------------------------------
    # 5.1 Pearson correlation of a symmetric parabola (y = x^2 over a
    #     symmetric range of x): close to 1, close to 0, or close to -1?
    #     Answer "close_to_zero", "close_to_one", or "close_to_negative_one".
    "parabola_pearson_magnitude": None,
    # 5.2 Spearman correlation of a monotone cubic (y = x^3): exactly what
    #     number?
    "monotone_spearman_value": None,
    # ----------------------------------------------------------------------
    # Exercise 6 -- Anscombe's quartet
    # ----------------------------------------------------------------------
    # 6.1 Do all four Anscombe sets share the same mean of x (to one
    #     decimal place)?
    "anscombe_means_agree": None,
    # 6.2 Does set IV have dramatically higher "leverage" on its one
    #     non-repeated x-value than set I?
    "anscombe_set_iv_leverage_dominant": None,
    # ----------------------------------------------------------------------
    # Exercise 7 -- Simpson's paradox
    # ----------------------------------------------------------------------
    # 7.1 Treatment A beats treatment B in BOTH subgroups. Does treatment B
    #     still win OVERALL?
    "simpson_b_wins_overall": None,
    # ----------------------------------------------------------------------
    # Exercise 8 -- robust spread under contamination
    # ----------------------------------------------------------------------
    # 8.1 3% contamination: does the standard deviation inflate by more
    #     than 5x?
    "contamination_inflates_std": None,
    # 8.2 Under the same contamination, does the median absolute deviation
    #     stay under 1.5x its clean value?
    "contamination_mad_stable": None,
    # ----------------------------------------------------------------------
    # Exercise 9 -- standardisation
    # ----------------------------------------------------------------------
    # 9.1 After standardising a sample, its mean is (approximately) what
    #     number?
    "standardized_mean": None,
    # 9.2 After standardising a sample, its standard deviation is
    #     (approximately) what number?
    "standardized_std": None,
    # 9.3 Does standardising CHANGE the Pearson correlation between two
    #     variables?
    "standardizing_changes_correlation": None,
}
