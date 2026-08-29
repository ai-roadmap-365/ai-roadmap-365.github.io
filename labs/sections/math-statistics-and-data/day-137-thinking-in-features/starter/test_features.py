"""Your exercises for Day 137 -- "Features That Do Not Cheat".

Nine exercises. Every test below currently calls `pytest.skip(...)` --
delete the skip line and replace it with real assertions. Read
`00_brief.md` for what each exercise is asking, `experiments.py` for the
measurement each one is about, and `features.py` for the encoders under
test.

Check yourself at any point:

    pytest starter -v

Never run `pytest starter examples` in one command -- both directories
hold a module named `test_features.py` and pytest collects by dotted
module name, so the two collide. Run them as two separate commands.

The reference answers live in `examples/test_features.py`. Read them
AFTER you have tried, never before.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import data
import experiments as E
import features as F
import models as M


# --- 1 ---------------------------------------------------------------------


def test_target_leakage_is_implausibly_good_and_removing_it_is_honest(leakage):
    """Exercise 1. `leakage` holds two scores for the same task.

    The table has one column, `days_to_first_invoice`, that cannot exist
    at prediction time: an invoice only happens after a visitor converts.

    Assert that:
      * `leakage["with_leak"]` is at least 0.99 -- implausibly good;
      * `leakage["without_leak"]` lands in an honest band, 0.55 to 0.80;
      * `leakage["gap_points"]` is at least 25.
    Then prove WHY it is a leak, straight from `data.signups()`: every
    unconverted row carries the sentinel -1 and every converted row
    carries a positive number.
    """
    pytest.skip("Exercise 1: assert the leaking score, the honest score and the gap.")


# --- 2 ---------------------------------------------------------------------


def test_fitting_before_the_split_costs_nothing_for_a_scaler_and_a_lot_for_an_imputer(
    scaler_contamination, imputer_contamination
):
    """Exercise 2. Two statistics fitted on all the data before splitting.

    Both fixtures average over many random splits, because with a small
    test set a single split says nothing.

    Assert that:
      * the scaler's `optimism_points` is smaller than 1 point in
        absolute value -- contaminating it buys essentially nothing;
      * the imputer's `contaminated` score beats its `correct` score,
        and `optimism_points` is at least 5;
      * the scaler's statistics really did differ: fit a `Standardiser`
        on all of `data.pricing()` and on 60 training rows, and assert
        the two `mean_[0]` values differ by more than 5.

    Ask yourself why the two differ so much. One of them applies a single
    affine map to both halves. The other does not.
    """
    pytest.skip("Exercise 2: measure the optimism from a contaminated scaler and imputer.")


# --- 3 ---------------------------------------------------------------------


def test_target_encoding_leaks_when_it_is_fitted_before_the_split(encoding):
    """Exercise 3. Replacing a category with the mean outcome uses the target.

    Assert that:
      * `naive_all_data` beats `out_of_fold`, by at least 4 points;
      * `out_of_fold` is at least as good as `naive_train_only`;
      * `naive_all_data` beats `naive_train_only` by at least 0.04.
    Then show the leak without a model in the way: build both encodings
    over the whole of `data.city_signups()` and assert the naive one
    correlates with the target above 0.25 while the out-of-fold one
    correlates below 0.10.
    """
    pytest.skip("Exercise 3: measure the naive and out-of-fold target encodings.")


# --- 4 ---------------------------------------------------------------------


def test_a_random_split_hides_what_a_time_ordered_split_shows(temporal):
    """Exercise 4. The same table, split at random and split by time.

    Assert that:
      * `random_split` is at least 0.80 and `time_ordered_split` is at
        most 0.20, a gap of at least 50 points;
      * the random training rows cover all 6 batches and the time-ordered
        ones cover 5, with exactly 1 test batch unseen;
      * the time-ordered score is BELOW the majority-class baseline for
        that period -- the model is not uninformed, it is confidently
        wrong.
    """
    pytest.skip("Exercise 4: compare the random and time-ordered splits.")


# --- 5 ---------------------------------------------------------------------


def test_cyclical_encoding_restores_the_adjacency_of_hour_23_and_hour_0(cyclical):
    """Exercise 5. Hour 23 and hour 0 are one hour apart. Prove it.

    This one is exact arithmetic, so assert exact values:
      * raw distance from 23 to 0 is 23.0, and from 3 to 4 is 1.0;
      * on the circle both are 2*sin(pi/24), to 1e-12;
      * the spread across all 24 adjacent pairs is under 1e-12;
      * hours 0 and 12 sit exactly 2.0 apart -- the circle's diameter.
    Then recompute the 24 adjacent distances yourself from
    `F.cyclical_encode(np.arange(24), 24)` rather than trusting the
    fixture, and assert they are all equal.
    """
    pytest.skip("Exercise 5: assert the raw and cyclical distances exactly.")


# --- 6 ---------------------------------------------------------------------


def test_an_ordinal_code_forces_an_order_that_one_hot_does_not(colours):
    """Exercise 6. Six paint colours, no order, one non-monotone outcome.

    Assert that:
      * `ordinal_is_monotone` is True and `one_hot_is_monotone` is False;
      * one-hot reproduces the observed per-colour rates to within 1e-5;
      * the ordinal model's largest error is above 0.30, and its accuracy
        is worse than one-hot's;
      * the observed rates really are not monotone in the code.
    """
    pytest.skip("Exercise 6: show that the ordinal model can only move monotonically.")


# --- 7 ---------------------------------------------------------------------


def test_a_ratio_separates_what_neither_column_separates(interaction):
    """Exercise 7. Spend and income overlap; spend over income does not.

    Assert the separation for all three: `ratio_only` is 1.0,
    `income_only` is under 0.60, `spend_only` is under 0.75, and the
    ratio beats the better component by at least 0.25.

    Then assert the honest footnote too: `income_and_spend` is at least
    0.95, because this particular boundary is a straight line through the
    origin and a linear model can find it from the raw columns.
    """
    pytest.skip("Exercise 7: report the separation for income, spend and the ratio.")


# --- 8 ---------------------------------------------------------------------


def test_the_vocabulary_must_be_chosen_on_training_documents_only(vocabulary):
    """Exercise 8. Which words become features is a fitted statistic too.

    Assert that:
      * `fitted_on_all_data` beats `fitted_on_train_only`, by at least
        1.5 points, averaged over 40 splits;
      * `unseen_test_words` is above zero, the matrix is exactly `top_k`
        columns wide and 100 rows tall -- unseen words are dropped, not
        crashed on.
    Then build a two-document vocabulary of your own, transform a
    document made entirely of words it has never seen, and assert you get
    a row of zeros rather than an exception.
    """
    pytest.skip("Exercise 8: measure the vocabulary leak and the unseen-word handling.")


# --- 9 ---------------------------------------------------------------------


def test_the_audit_catches_the_planted_leaks_and_leaves_honest_columns_alone(audit):
    """Exercise 9. Turn the day into a check you can run on any table.

    `E.audit_table()` is the signups table plus two extra columns: a
    categorical leak (`email_template`) and an honest one (`channel`).

    Assert that:
      * exactly `days_to_first_invoice` and `email_template` are flagged,
        by the `separable` and `pure_category` rules respectively;
      * none of `visits`, `minutes_on_site`, `discount_pct` or `channel`
        is flagged, and all four were actually checked;
      * the numeric leak's absolute correlation with the target is
        between 0.80 and 0.90 -- UNDER the default threshold, so the
        correlation rule alone would have missed it;
      * with `corr_threshold=1.01`, which disables the correlation rule
        completely, both leaks are still caught.
    """
    pytest.skip("Exercise 9: assert the audit catches the planted leaks and nothing else.")
