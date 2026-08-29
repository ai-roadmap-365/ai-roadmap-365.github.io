"""YOUR test suite for Day 125 -- "Cleaning With Receipts". Nine exercises.

Run it from the lab directory, not from here:

    pytest starter -v

Every exercise below ends in a `pytest.skip(...)` line. pytest reports a
skip as `s` in the dot line and moves on, so an unfinished suite still
exits 0. Replace each skip with real assertions -- deleting the skip line
is part of the exercise. `starter/00_brief.md` explains each exercise in
full; the fixtures you need come from `conftest.py` and are described
there too.

Assert exact values everywhere except where the brief says approx is
appropriate (the imputation statistics use pytest.approx because they are
floating-point arithmetic, not because the day is one machine on one day).
"""

import numpy as np
import pandas as pd
import pytest

from contract import ContractViolation, assert_cleaning_contract

# --------------------------------------------------------------------------
# EXERCISE 1 -- mean imputation distorts. See starter/00_brief.md exercise 1.
#
# Check with:   pytest starter -v -k test_1
# --------------------------------------------------------------------------


def test_1_mean_survives_imputation_unchanged(income_spending):
    pytest.skip(
        "exercise 1a: assert income.mean() before and after fillna(mean) match "
        "within pytest.approx(..., abs=1e-6) of each other"
    )


def test_1_std_strictly_shrinks(income_spending):
    pytest.skip(
        "exercise 1b: assert income.std() strictly decreases after mean imputation"
    )


def test_1_correlation_strictly_attenuates_not_inflates(income_spending):
    pytest.skip(
        "exercise 1c: assert abs(corr(income, spending)) strictly decreases after "
        "mean-imputing income -- NOT increases; see 00_brief.md for why the direction "
        "is forced, not a guess"
    )


def test_1_n_missing_matches_the_planted_count(income_spending):
    pytest.skip("exercise 1d: assert income_spending['income'].isna().sum() == 10")


# --------------------------------------------------------------------------
# EXERCISE 2 -- fillna(0) on a measurement column. Zero is a value.
#
# Check with:   pytest starter -v -k test_2
# --------------------------------------------------------------------------


def test_2_fillna_zero_moves_the_mean_by_the_exact_amount(temperature_readings):
    pytest.skip(
        "exercise 2a: assert the mean before and after fillna(0.0), and the exact "
        "(negative) shift between them"
    )


def test_2_fillna_zero_confuses_missing_with_a_real_zero_reading(temperature_readings):
    pytest.skip(
        "exercise 2b: row index 9 is a GENUINE 0.0C reading, not missing. After "
        "fillna(0), assert it is bit-for-bit indistinguishable from the three rows "
        "that really were missing"
    )


# --------------------------------------------------------------------------
# EXERCISE 3 -- dropna with how, thresh, subset.
#
# Check with:   pytest starter -v -k test_3
# --------------------------------------------------------------------------


def test_3_dropna_row_counts(dropna_frame):
    pytest.skip(
        "exercise 3: on the 8-row dropna_frame, assert the row counts for "
        "how='any', how='all', thresh=2, and subset=['email']"
    )


# --------------------------------------------------------------------------
# EXERCISE 4 -- ffill on unsorted data is a real bug.
#
# Check with:   pytest starter -v -k test_4
# --------------------------------------------------------------------------


def test_4_ffill_on_unsorted_data_is_wrong(sensor_timeseries):
    pytest.skip(
        "exercise 4a: shuffle_rows(sensor_timeseries, seed=7), ffill WITHOUT sorting "
        "first, and assert day 2 and day 3 come out wrong (compare against the "
        "sorted-then-filled correct answer)"
    )


def test_4_ffill_after_sorting_is_correct(sensor_timeseries):
    pytest.skip(
        "exercise 4b: shuffle, sort_values('day'), THEN ffill; assert the full "
        "reading column equals [10.0, 10.0, 10.0, 13.0, 14.0, 14.0, 16.0, 17.0]"
    )


# --------------------------------------------------------------------------
# EXERCISE 5 -- the missing indicator.
#
# Check with:   pytest starter -v -k test_5
# --------------------------------------------------------------------------


def test_5_missing_indicator_exactly_matches_original_mask(temperature_readings):
    pytest.skip(
        "exercise 5: record isna() into a new column BEFORE imputing, then impute "
        "with the mean; assert the recorded column still equals the ORIGINAL isna() "
        "mask, even though reading_c.isna() is now all False"
    )


# --------------------------------------------------------------------------
# EXERCISE 6 -- to_numeric(errors='coerce').
#
# Check with:   pytest starter -v -k test_6
# --------------------------------------------------------------------------


def test_6_coerce_count_matches_the_planted_garbage(coerce_frame):
    pytest.skip(
        "exercise 6: pd.to_numeric(coerce_frame['quantity_raw'], errors='coerce'); "
        "assert the resulting NaN count equals the count of the three planted garbage "
        "strings ('N/A', 'unknown', '--'), and that the clean values survive as floats"
    )


# --------------------------------------------------------------------------
# EXERCISE 7 -- string normalisation.
#
# Check with:   pytest starter -v -k test_7
# --------------------------------------------------------------------------


def test_7_nunique_before_and_after_normalisation(country_frame):
    pytest.skip(
        "exercise 7a: assert country_raw.nunique() is 8 before normalising "
        "(.str.strip().str.lower().str.replace('.', '', regex=False), then map "
        "'usa'->'USA', 'canada'->'Canada'), and 2 after"
    )


def test_7_raw_groupby_splits_one_true_country_into_several(country_frame):
    pytest.skip(
        "exercise 7b: assert groupby('country_raw') produces 8 groups (wrong -- the "
        "truth is 2), then assert the normalised groupby produces 2 groups with the "
        "correct USA/Canada amount totals"
    )


# --------------------------------------------------------------------------
# EXERCISE 8 -- duplicates mean whatever subset you named.
#
# Check with:   pytest starter -v -k test_8
# --------------------------------------------------------------------------


def test_8_exact_and_subset_duplicate_counts_differ(duplicates_frame):
    pytest.skip(
        "exercise 8a: assert duplicated().sum() and duplicated(subset=['customer_id', "
        "'item']).sum() are different exact counts, and that the subset count is larger"
    )


def test_8_which_definition_is_right_depends_on_the_question(duplicates_frame):
    pytest.skip(
        "exercise 8b: identify which customer_id(s) the exact-duplicate definition "
        "flags, and which the subset definition flags, and assert both sets exactly"
    )


# --------------------------------------------------------------------------
# EXERCISE 9 -- the cleaning contract must hold AND be provably able to fail.
#
# Check with:   pytest starter -v -k test_9
# --------------------------------------------------------------------------


def test_9_contract_passes_on_clean_data(clean_customers):
    pytest.skip(
        "exercise 9a: call assert_cleaning_contract on clean_customers with "
        "key_columns=['customer_id', 'country'], dtypes={'income': 'float64'}, "
        "min_rows=3, max_rows=10; it must NOT raise"
    )


def test_9_contract_raises_on_a_null_key_column(contract_violating_customers):
    pytest.skip(
        "exercise 9b: with pytest.raises(ContractViolation, match='customer_id'), "
        "call the same contract on contract_violating_customers"
    )


def test_9_contract_raises_on_a_wrong_dtype():
    pytest.skip(
        "exercise 9c: take build_clean_customers(), cast income to str, and assert "
        "the contract raises ContractViolation matching 'income'"
    )


def test_9_contract_raises_on_a_row_count_outside_the_range():
    pytest.skip(
        "exercise 9d: take build_clean_customers().iloc[:1] (1 row) and assert the "
        "contract raises ContractViolation matching 'row count'"
    )
