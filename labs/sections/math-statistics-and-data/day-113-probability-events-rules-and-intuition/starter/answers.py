"""Exercises 1 through 9 -- eighteen predictions.

Replace each `None` with the value you think is correct. A `None` is a skip,
not a failure: `pytest starter -q` counts only what you have attempted. When
you are wrong it prints both your answer and the real one, so a wrong guess
is worth more than a blank.

Predict BEFORE you run anything. The two that catch almost everyone are the
addition-rule error amount (exercise 2) and de Méré's favourable bet
(exercise 3) -- and they only catch you if you commit first.

Every answer is a number, a Python bool, or (for one question) an int naming
a bet.
"""

ANSWERS: dict[str, object] = {
    # ----------------------------------------------------------------------
    # Exercise 1 -- the sample space
    # ----------------------------------------------------------------------
    # 1.1 How many outcomes are in the sample space of two dice?
    "sample_space_size": None,
    # 1.2 P(the two dice sum to 7), as a decimal.
    "p_sum_seven": None,
    # ----------------------------------------------------------------------
    # Exercise 2 -- the addition rule
    # ----------------------------------------------------------------------
    # 2.1 A = "sum is 7" (6 outcomes), B = "first die is 6" (6 outcomes).
    #     The WRONG naive sum P(A) + P(B), as a decimal.
    "addition_naive_sum": None,
    # 2.2 The TRUE P(A or B), as a decimal.
    "addition_true_union": None,
    # 2.3 By exactly how much does the naive sum overstate the truth?
    "addition_error_amount": None,
    # ----------------------------------------------------------------------
    # Exercise 3 -- de Méré's two bets
    # ----------------------------------------------------------------------
    # 3.1 P(at least one 6 in 4 rolls of one die), as a decimal.
    "de_mere_single_bet_probability": None,
    # 3.2 P(at least one double-six in 24 rolls of two dice), as a decimal.
    "de_mere_double_bet_probability": None,
    # 3.3 Which bet is favourable to the player (probability above 0.5)?
    #     Answer 1 or 2.
    "de_mere_favorable_bet": None,
    # ----------------------------------------------------------------------
    # Exercise 4 -- independence
    # ----------------------------------------------------------------------
    # 4.1 Does P(A and B) == P(A) * P(B) hold for the INDEPENDENT_PAIR?
    "independent_pair_holds": None,
    # 4.2 Does it hold for the DEPENDENT_PAIR?
    "dependent_pair_holds": None,
    # ----------------------------------------------------------------------
    # Exercise 5 -- mutual exclusivity implies dependence
    # ----------------------------------------------------------------------
    # 5.1 For the mutually exclusive pair (sum = 2, sum = 12), is
    #     P(sum=2 | sum=12) == 0 while P(sum=2) != 0 -- i.e. are they
    #     dependent?
    "mutually_exclusive_implies_dependent": None,
    # ----------------------------------------------------------------------
    # Exercise 6 -- conditioning by restriction
    # ----------------------------------------------------------------------
    # 6.1 P(sum = 8 | first die is even), as a decimal.
    "conditional_p_sum8_given_first_even": None,
    # 6.2 Does the formula method and the filter-the-space method agree
    #     exactly?
    "conditional_formula_matches_filter": None,
    # ----------------------------------------------------------------------
    # Exercise 7 -- the law of total probability
    # ----------------------------------------------------------------------
    # 7.1 P(red), across both urns, weighted by the fair coin. As a decimal.
    "urn_total_probability_red": None,
    # 7.2 Does the weighted-total answer match the answer from enumerating
    #     the combined 20-outcome experiment directly?
    "urn_enumeration_matches_formula": None,
    # ----------------------------------------------------------------------
    # Exercise 8 -- Monte Carlo error scaling
    # ----------------------------------------------------------------------
    # 8.1 Does the average simulation error shrink as the sample size grows
    #     from 100 to 100,000?
    "monte_carlo_error_shrinks_with_n": None,
    # 8.2 Multiplying n by 10 should shrink the error by roughly sqrt(10),
    #     not by 10. Is the OBSERVED shrink much closer to sqrt(10) than
    #     to 10?
    "monte_carlo_error_ratio_near_sqrt10": None,
    # ----------------------------------------------------------------------
    # Exercise 9 -- reproducibility
    # ----------------------------------------------------------------------
    # 9.1 Two simulations with the SAME seed: byte-identical results?
    "reproducibility_same_seed_identical": None,
    # 9.2 Two simulations with DIFFERENT seeds: different results that both
    #     still land within tolerance of the true probability?
    "reproducibility_different_seed_differs": None,
}
