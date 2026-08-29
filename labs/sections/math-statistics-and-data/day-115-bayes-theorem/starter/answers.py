"""Exercises 1 through 9 -- fifteen predictions.

Replace each `None` with the value you think is correct. A `None` is a skip,
not a failure: `pytest starter -q` counts only what you have attempted. When
you are wrong it prints both your answer and the real one, so a wrong guess
is worth more than a blank.

Predict BEFORE you run anything. The two that catch almost everyone: the
opening posterior (exercise 1) and the naive-versus-correlated gap
(exercise 7) -- and they only catch you if you commit to a number first.

Every answer is a number (as a plain float), a Python bool, or (for one
question) a short string naming a class.
"""

ANSWERS: dict[str, object] = {
    # ----------------------------------------------------------------------
    # Exercise 1 -- the opening posterior
    # ----------------------------------------------------------------------
    # 1.1 P(condition | positive), 99% sensitive/specific test, 1-in-1000
    #     prevalence, as a decimal.
    "opening_posterior": None,
    # 1.2 Is the true posterior LOWER than the naive 0.99 guess?
    "opening_posterior_below_naive_guess": None,
    # ----------------------------------------------------------------------
    # Exercise 2 -- natural frequencies
    # ----------------------------------------------------------------------
    # 2.1 Out of 100,000 people, how many test positive in total (true
    #     positives + false positives)?
    "natural_frequency_total_positives": None,
    # ----------------------------------------------------------------------
    # Exercise 3 -- simulation
    # ----------------------------------------------------------------------
    # 3.1 Does the simulated posterior land within 3 standard errors of the
    #     exact value at n = 2,000,000?
    "simulation_within_tolerance": None,
    # ----------------------------------------------------------------------
    # Exercise 4 -- the prevalence sweep
    # ----------------------------------------------------------------------
    # 4.1 At prevalence = 1/2, what is the posterior, as a decimal?
    "prevalence_half_posterior": None,
    # 4.2 Is the posterior strictly increasing as prevalence rises?
    "prevalence_sweep_increasing": None,
    # ----------------------------------------------------------------------
    # Exercise 5 -- the odds form
    # ----------------------------------------------------------------------
    # 5.1 What is the likelihood ratio LR+ for the 99%/99% test?
    "likelihood_ratio_value": None,
    # 5.2 Does posterior_odds == prior_odds * likelihood_ratio hold exactly?
    "odds_form_matches_direct": None,
    # ----------------------------------------------------------------------
    # Exercise 6 -- sequential updating
    # ----------------------------------------------------------------------
    # 6.1 Two different positive tests (A then B), posterior as a decimal.
    "sequential_two_test_posterior": None,
    # 6.2 Does updating with B first, then A, give the identical result?
    "sequential_order_independent": None,
    # ----------------------------------------------------------------------
    # Exercise 7 -- correlated tests
    # ----------------------------------------------------------------------
    # 7.1 The naive (assumes-independence) posterior for two same-sample
    #     positive results, as a decimal.
    "correlated_naive_posterior": None,
    # 7.2 Is the naive posterior STRICTLY HIGHER than the correct,
    #     correlation-aware posterior?
    "correlated_naive_overstates": None,
    # ----------------------------------------------------------------------
    # Exercise 8 -- Naive Bayes with Laplace smoothing
    # ----------------------------------------------------------------------
    # 8.1 With smoothing, what class does the veto-case document
    #     ("please review schedule watches") get classified as?
    "veto_case_smoothed_class": None,
    # 8.2 Without smoothing, is ham's score EXACTLY zero for that document?
    "veto_case_unsmoothed_ham_is_zero": None,
    # ----------------------------------------------------------------------
    # Exercise 9 -- log space
    # ----------------------------------------------------------------------
    # 9.1 Does multiplying 500 factors of 0.01 as plain floats underflow to
    #     exactly 0.0?
    "underflow_to_exactly_zero": None,
}
