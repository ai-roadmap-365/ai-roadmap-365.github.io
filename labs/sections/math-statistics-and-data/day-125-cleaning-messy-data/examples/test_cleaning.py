"""The worked reference suite for Day 125 -- "Cleaning With Receipts".

Nine exercises, each proving one real pandas 3.0.5 cleaning behaviour by
running code and reading real values -- never by reading source. Run it:

    pytest examples

Every table these tests use comes from `data.py`, imported through the
fixtures in `conftest.py`. Read `starter/00_brief.md` for the exercise-by-
exercise explanation; this file is the answer key.
"""

import numpy as np
import pandas as pd
import pytest

from contract import ContractViolation, assert_cleaning_contract

# --------------------------------------------------------------------------
# Exercise 1 -- mean imputation distorts. The mean survives untouched; the
# standard deviation strictly shrinks; and -- contrary to the intuitive
# guess that a "pile of average points" inflates a correlation -- the
# correlation with a genuinely related column strictly ATTENUATES (moves
# toward zero), never grows. See this lab's README and the lesson's "Why
# this matters" section for why that direction is mathematically forced,
# not a coincidence of this one dataset.
# --------------------------------------------------------------------------


def test_1_mean_survives_imputation_unchanged(income_spending):
    before_mean = income_spending["income"].mean()
    imputed = income_spending["income"].fillna(before_mean)
    after_mean = imputed.mean()

    assert before_mean == pytest.approx(52_666.679, abs=0.01)
    assert after_mean == pytest.approx(before_mean, abs=1e-6)


def test_1_std_strictly_shrinks(income_spending):
    before_std = income_spending["income"].std()
    imputed = income_spending["income"].fillna(income_spending["income"].mean())
    after_std = imputed.std()

    assert before_std == pytest.approx(10_663.947, abs=0.01)
    assert after_std == pytest.approx(9_195.697, abs=0.01)
    assert after_std < before_std, "imputation must strictly shrink the standard deviation"


def test_1_correlation_strictly_attenuates_not_inflates(income_spending):
    before_corr = income_spending[["income", "spending"]].corr().iloc[0, 1]

    after = income_spending.copy()
    after["income"] = after["income"].fillna(after["income"].mean())
    after_corr = after[["income", "spending"]].corr().iloc[0, 1]

    assert before_corr == pytest.approx(0.745156, abs=1e-4)
    assert after_corr == pytest.approx(0.606148, abs=1e-4)
    assert abs(after_corr) < abs(before_corr), (
        "mean imputation must strictly shrink the correlation's magnitude, not grow it -- "
        "an imputed point sits exactly at the column mean, so it contributes zero to the "
        "covariance and zero to its own column's variance term, and can only dilute an "
        "existing relationship, never strengthen one"
    )


def test_1_n_missing_matches_the_planted_count(income_spending):
    assert income_spending["income"].isna().sum() == 10


# --------------------------------------------------------------------------
# Exercise 2 -- fillna(0) on a measurement column. Zero is a value, not an
# absence: a station's real 0.0C reading and a MISSING reading must not be
# collapsed into the same number.
# --------------------------------------------------------------------------


def test_2_fillna_zero_moves_the_mean_by_the_exact_amount(temperature_readings):
    before_mean = temperature_readings["reading_c"].mean()
    after_mean = temperature_readings["reading_c"].fillna(0.0).mean()

    assert before_mean == pytest.approx(10.657143, abs=1e-4)
    assert after_mean == pytest.approx(7.46, abs=1e-4)

    shift = after_mean - before_mean
    assert shift == pytest.approx(-3.197143, abs=1e-4)
    assert shift != 0.0, "filling with 0 must move the mean -- 0 is a real value, not a no-op"


def test_2_fillna_zero_confuses_missing_with_a_real_zero_reading(temperature_readings):
    # Station C's row 9 (index 9) is a GENUINE 0.0C reading, already present
    # before any fill. After fillna(0), it is indistinguishable from the
    # three rows that were actually missing.
    genuine_zero_before = temperature_readings.loc[9, "reading_c"]
    assert genuine_zero_before == 0.0
    assert not pd.isna(genuine_zero_before)

    filled = temperature_readings["reading_c"].fillna(0.0)
    was_missing = temperature_readings["reading_c"].isna()
    now_all_read_as_zero_or_real = (filled[was_missing] == 0.0).all()
    assert now_all_read_as_zero_or_real
    # The three imputed rows and the one genuine zero are now bit-for-bit
    # identical in the data -- nothing downstream can tell them apart.
    assert (filled == 0.0).sum() == was_missing.sum() + 1


# --------------------------------------------------------------------------
# Exercise 3 -- dropna with how, thresh and subset give four different row
# counts on the same eight-row frame.
# --------------------------------------------------------------------------


def test_3_dropna_row_counts(dropna_frame):
    assert dropna_frame.shape == (8, 4)

    how_any = dropna_frame.dropna(how="any")
    how_all = dropna_frame.dropna(how="all")
    thresh_2 = dropna_frame.dropna(thresh=2)
    subset_email = dropna_frame.dropna(subset=["email"])

    assert how_any.shape[0] == 2, "how='any' drops any row missing even one field -- the strictest cut"
    assert how_all.shape[0] == 8, "how='all' only drops a row missing on EVERY field -- none here are"
    assert thresh_2.shape[0] == 5, "thresh=2 keeps rows with at least 2 non-null fields"
    assert subset_email.shape[0] == 4, "subset=['email'] only checks the named column"


# --------------------------------------------------------------------------
# Exercise 4 -- ffill on unsorted data is a real bug. The wrong answer
# appears on the unsorted frame; sorting first fixes it.
# --------------------------------------------------------------------------


def test_4_ffill_on_unsorted_data_is_wrong(sensor_timeseries):
    from data import shuffle_rows

    shuffled = shuffle_rows(sensor_timeseries, seed=7)
    wrong = shuffled.copy()
    wrong["reading"] = wrong["reading"].ffill()

    # Re-sort by day only to COMPARE against the correct answer -- the
    # ffill computation itself already happened on the unsorted frame.
    wrong_by_day = wrong.sort_values("day").reset_index(drop=True)

    correct = sensor_timeseries.sort_values("day").reset_index(drop=True)
    correct["reading"] = correct["reading"].ffill()

    assert wrong_by_day.loc[wrong_by_day["day"] == 2, "reading"].item() == 14.0
    assert correct.loc[correct["day"] == 2, "reading"].item() == 10.0
    assert wrong_by_day.loc[wrong_by_day["day"] == 3, "reading"].item() == 17.0
    assert correct.loc[correct["day"] == 3, "reading"].item() == 10.0

    differing_days = wrong_by_day.loc[wrong_by_day["reading"] != correct["reading"], "day"].tolist()
    assert differing_days == [2, 3]


def test_4_ffill_after_sorting_is_correct(sensor_timeseries):
    from data import shuffle_rows

    shuffled = shuffle_rows(sensor_timeseries, seed=7)
    fixed = shuffled.sort_values("day").reset_index(drop=True)
    fixed["reading"] = fixed["reading"].ffill()

    expected = [10.0, 10.0, 10.0, 13.0, 14.0, 14.0, 16.0, 17.0]
    assert fixed["reading"].tolist() == expected


# --------------------------------------------------------------------------
# Exercise 5 -- the missing indicator. Record WHICH values were imputed
# before the imputation erases the evidence, and confirm the flag column
# is an exact record of the original isna() mask.
# --------------------------------------------------------------------------


def test_5_missing_indicator_exactly_matches_original_mask(temperature_readings):
    reading_was_missing = temperature_readings["reading_c"].isna()

    cleaned = temperature_readings.copy()
    cleaned["reading_c_was_missing"] = reading_was_missing
    cleaned["reading_c"] = cleaned["reading_c"].fillna(cleaned["reading_c"].mean())

    # After imputation, isna() alone can no longer tell you anything --
    # every value looks "present" now.
    assert cleaned["reading_c"].isna().sum() == 0

    # But the indicator column still says exactly what isna() said before
    # the fill erased the evidence.
    assert cleaned["reading_c_was_missing"].sum() == 3
    assert (cleaned["reading_c_was_missing"] == reading_was_missing).all()


# --------------------------------------------------------------------------
# Exercise 6 -- to_numeric(errors="coerce") converts every unparseable
# string into a missing value, silently. Count them; never coerce blind.
# --------------------------------------------------------------------------


def test_6_coerce_count_matches_the_planted_garbage(coerce_frame):
    coerced = pd.to_numeric(coerce_frame["quantity_raw"], errors="coerce")

    n_coerced = coerced.isna().sum()
    planted_garbage = coerce_frame["quantity_raw"].isin(["N/A", "unknown", "--"]).sum()

    assert n_coerced == 3
    assert planted_garbage == 3
    assert n_coerced == planted_garbage, "every coerced NaN must trace back to a planted garbage string"

    # The clean values must survive the coercion exactly, as floats.
    clean_values = coerced.dropna().tolist()
    assert clean_values == [12.0, 7.0, 3.0, 9.0, 5.0, 20.0, 4.0]


# --------------------------------------------------------------------------
# Exercise 7 -- string normalisation. One country, four raw spellings; a
# raw groupby silently produces more groups than the truth.
# --------------------------------------------------------------------------


def test_7_nunique_before_and_after_normalisation(country_frame):
    before = country_frame["country_raw"].nunique()
    assert before == 8

    normalised = (
        country_frame["country_raw"]
        .str.strip()
        .str.lower()
        .str.replace(".", "", regex=False)
        .replace({"usa": "USA", "canada": "Canada"})
    )
    after = normalised.nunique()
    assert after == 2
    assert set(normalised.unique()) == {"USA", "Canada"}


def test_7_raw_groupby_splits_one_true_country_into_several(country_frame):
    raw_groups = country_frame.groupby("country_raw")["amount"].sum()
    assert len(raw_groups) == 8  # the true count is 2

    normalised = (
        country_frame["country_raw"]
        .str.strip()
        .str.lower()
        .str.replace(".", "", regex=False)
        .replace({"usa": "USA", "canada": "Canada"})
    )
    true_groups = country_frame.assign(country=normalised).groupby("country")["amount"].sum()
    assert len(true_groups) == 2
    assert true_groups.loc["USA"] == pytest.approx(865.0)
    assert true_groups.loc["Canada"] == pytest.approx(215.0)


# --------------------------------------------------------------------------
# Exercise 8 -- duplicates. "Duplicate" means whatever subset you named.
# --------------------------------------------------------------------------


def test_8_exact_and_subset_duplicate_counts_differ(duplicates_frame):
    exact_dupes = duplicates_frame.duplicated().sum()
    subset_dupes = duplicates_frame.duplicated(subset=["customer_id", "item"]).sum()

    assert exact_dupes == 1, "row 4 exactly repeats row 0 (customer, item, price AND timestamp)"
    assert subset_dupes == 2, (
        "row 4 repeats row 0's (customer_id, item), and row 5 repeats row 1's "
        "(customer_id, item) even though row 5's timestamp differs"
    )
    assert subset_dupes > exact_dupes, (
        "'duplicate on a subset' is a strictly looser question than 'duplicate on every "
        "column', so it can only find as many or more rows"
    )


def test_8_which_definition_is_right_depends_on_the_question(duplicates_frame):
    # Question: "did this exact order get logged twice?" -- exact duplicates
    # is right, because a genuine re-order at the same second with the same
    # price is (at these row counts) indistinguishable from a duplicate log
    # entry.
    exact = duplicates_frame[duplicates_frame.duplicated()]
    assert exact["customer_id"].tolist() == [1]

    # Question: "did this customer buy this item more than once?" -- subset
    # duplicates on (customer_id, item) is right, because customer 2's two
    # mug purchases on different days are two real events, not one row
    # logged twice, and only the subset definition catches both repeats.
    subset = duplicates_frame[duplicates_frame.duplicated(subset=["customer_id", "item"])]
    assert sorted(subset["customer_id"].tolist()) == [1, 2]


# --------------------------------------------------------------------------
# Exercise 9 -- the cleaning contract. Post-conditions hold on cleaned
# data, and the contract genuinely RAISES on data that violates it.
# --------------------------------------------------------------------------


def test_9_contract_passes_on_clean_data(clean_customers):
    # Must not raise.
    assert_cleaning_contract(
        clean_customers,
        key_columns=["customer_id", "country"],
        dtypes={"income": "float64"},
        min_rows=3,
        max_rows=10,
    )


def test_9_contract_raises_on_a_null_key_column(contract_violating_customers):
    with pytest.raises(ContractViolation, match="customer_id"):
        assert_cleaning_contract(
            contract_violating_customers,
            key_columns=["customer_id", "country"],
            dtypes={"income": "float64"},
            min_rows=3,
            max_rows=10,
        )


def test_9_contract_raises_on_a_wrong_dtype():
    from data import build_clean_customers

    wrong_dtype = build_clean_customers()
    wrong_dtype["income"] = wrong_dtype["income"].astype(str)

    with pytest.raises(ContractViolation, match="income"):
        assert_cleaning_contract(
            wrong_dtype,
            key_columns=["customer_id", "country"],
            dtypes={"income": "float64"},
            min_rows=3,
            max_rows=10,
        )


def test_9_contract_raises_on_a_row_count_outside_the_range():
    from data import build_clean_customers

    too_few_rows = build_clean_customers().iloc[:1]

    with pytest.raises(ContractViolation, match="row count"):
        assert_cleaning_contract(
            too_few_rows,
            key_columns=["customer_id", "country"],
            dtypes={"income": "float64"},
            min_rows=3,
            max_rows=10,
        )
