"""YOUR test suite for Day 124 -- "Joins That Keep Their Shape". Nine exercises.

Run it from the lab directory, not from here:

    pytest starter -v

Every exercise below ends in a `pytest.skip(...)` line. pytest reports a
skip as `s` in the dot line and moves on, so an unfinished suite still
exits 0. Replace each skip with real assertions -- deleting the skip line
is part of the exercise. `starter/00_brief.md` explains each exercise in
full; the fixtures you need (`left_dup`, `right_dup`, `left_keys`,
`right_keys`, `int_keyed`, `str_keyed`, `price_left`, `price_right`,
`wide`, `dup_index_col`) come from `conftest.py` and are described there
too.

Assert exact values everywhere in this lab -- there is no timing
assertion here the way Day 123 had one.
"""

import numpy as np
import pandas as pd
import pytest

# --------------------------------------------------------------------------
# EXERCISE 1 -- the explosion. See starter/00_brief.md exercise 1.
#
# Check with:   pytest starter -v -k test_1
# --------------------------------------------------------------------------


def test_1_many_to_many_merge_produces_the_per_key_product(left_dup, right_dup):
    pytest.skip(
        "exercise 1: merge left_dup and right_dup inner on cust_id; compute the "
        "expected row count from each side's per-key value_counts product and "
        "assert the merged shape matches it exactly (14 rows); also assert key "
        "A alone produces 6 rows and key B alone produces 8"
    )


# --------------------------------------------------------------------------
# EXERCISE 2 -- validate=. See starter/00_brief.md exercise 2.
#
# Check with:   pytest starter -v -k test_2
# --------------------------------------------------------------------------


def test_2_validate_one_to_one_raises_on_duplicated_keys(left_dup, right_dup):
    pytest.skip(
        "exercise 2a: assert merging left_dup and right_dup with "
        "validate='one_to_one' raises pandas.errors.MergeError"
    )


def test_2_validate_one_to_one_passes_on_genuinely_unique_keys(left_keys, right_keys):
    pytest.skip(
        "exercise 2b: assert merging left_keys and right_keys with "
        "validate='one_to_one' raises nothing and returns 3 rows"
    )


def test_2_validate_one_to_many_raises_when_the_many_side_is_actually_duplicated_on_both(left_dup, right_dup):
    pytest.skip(
        "exercise 2c: assert validate='one_to_many' on left_dup/right_dup also "
        "raises MergeError, because key A repeats on the LEFT side too"
    )


# --------------------------------------------------------------------------
# EXERCISE 3 -- indicator=True. See starter/00_brief.md exercise 3.
#
# Check with:   pytest starter -v -k test_3
# --------------------------------------------------------------------------


def test_3_indicator_counts_reconcile_with_the_inputs(left_keys, right_keys):
    pytest.skip(
        "exercise 3: outer merge left_keys/right_keys with indicator=True; assert "
        "left_only=1, right_only=1, both=3, and that left_only+both == 4 "
        "(left_keys row count), right_only+both == 4 (right_keys row count), and "
        "all three sum to the merged row count (5)"
    )


# --------------------------------------------------------------------------
# EXERCISE 4 -- the silent dtype-mismatch join. See starter/00_brief.md
# exercise 4.
#
# Check with:   pytest starter -v -k test_4
# --------------------------------------------------------------------------


def test_4_dtype_mismatch_join_returns_zero_rows(int_keyed, str_keyed):
    pytest.skip(
        "exercise 4a: confirm int_keyed['id'] is int64 and str_keyed['id'] is "
        "category; inner-merge them on 'id' and assert the result has 0 rows "
        "and the correct columns, with no exception raised"
    )


def test_4_casting_one_side_fixes_it(int_keyed, str_keyed):
    pytest.skip(
        "exercise 4b: cast str_keyed['id'] to int64 with .astype, merge again, "
        "and assert 3 rows with id 1002's score equal to 91"
    )


def test_4_plain_str_key_against_int64_raises_instead_of_matching_nothing(int_keyed):
    pytest.skip(
        "exercise 4c: build a fresh DataFrame with a plain str 'id' column of "
        "the same digits ('1001','1002','1003') and a 'score' column, and "
        "assert merging it against int_keyed on 'id' raises ValueError -- this "
        "is a real correction to the classic silent-zero-rows story"
    )


# --------------------------------------------------------------------------
# EXERCISE 5 -- the four join types on one pair of frames. See
# starter/00_brief.md exercise 5.
#
# Check with:   pytest starter -v -k test_5
# --------------------------------------------------------------------------


def test_5_inner_keeps_only_the_overlap(left_keys, right_keys):
    pytest.skip("exercise 5a: how='inner' on left_keys/right_keys gives 3 rows, keys B, C, D")


def test_5_left_keeps_every_left_row(left_keys, right_keys):
    pytest.skip(
        "exercise 5b: how='left' gives 4 rows, keys A-D, with A's 'plan' all NaN"
    )


def test_5_right_keeps_every_right_row(left_keys, right_keys):
    pytest.skip(
        "exercise 5c: how='right' gives 4 rows, keys B-E, with E's 'region' all NaN"
    )


def test_5_outer_keeps_every_row_from_both(left_keys, right_keys):
    pytest.skip("exercise 5d: how='outer' gives 5 rows, keys A-E")


def test_5_row_counts_in_one_table(left_keys, right_keys):
    pytest.skip(
        "exercise 5e: build a dict of {how: row_count} for inner/left/right/outer "
        "and assert it equals {'inner': 3, 'left': 4, 'right': 4, 'outer': 5}"
    )


# --------------------------------------------------------------------------
# EXERCISE 6 -- suffixes, on/left_on/right_on, and join(). See
# starter/00_brief.md exercise 6.
#
# Check with:   pytest starter -v -k test_6
# --------------------------------------------------------------------------


def test_6_default_suffixes_are_x_and_y(price_left, price_right):
    pytest.skip(
        "exercise 6a: merge price_left/price_right on 'sku'; assert 'price_x' "
        "and 'price_y' exist and 'price' does not, with X1's values 9.99/10.99"
    )


def test_6_explicit_suffixes_rename_as_asked(price_left, price_right):
    pytest.skip(
        "exercise 6b: repeat with suffixes=('_catalog', '_live'); assert those "
        "column names exist instead and X2's values are 14.50/13.00"
    )


def test_6_on_versus_left_on_right_on_give_the_same_result(price_left, price_right):
    pytest.skip(
        "exercise 6c: rename price_right's 'sku' to 'sku_code', merge once with "
        "on='sku' and once with left_on='sku'/right_on='sku_code', and assert "
        "both give the same row count and the same price_l values"
    )


def test_6_join_on_index_matches_merge_on_column(price_left, price_right):
    pytest.skip(
        "exercise 6d: set_index('sku') on both frames and use .join(how='inner', "
        "lsuffix='_l', rsuffix='_r'); assert it equals the equivalent .merge(on='sku') "
        "result, once both are sorted by index"
    )


# --------------------------------------------------------------------------
# EXERCISE 7 -- concat alignment. See starter/00_brief.md exercise 7.
#
# Check with:   pytest starter -v -k test_7
# --------------------------------------------------------------------------


def test_7_concat_axis_0_with_mismatched_columns_fills_nan():
    pytest.skip(
        "exercise 7a: build frame_a={'a':[1,2],'b':[3,4]} and frame_b={'b':[5,6],'c':[7,8]}; "
        "pd.concat([frame_a, frame_b], axis=0, ignore_index=True); assert shape (4,3), "
        "frame_a's rows have NaN in 'c', frame_b's rows have NaN in 'a', and 'b' is "
        "never NaN"
    )


def test_7_concat_axis_1_with_mismatched_index_fills_nan():
    pytest.skip(
        "exercise 7b: build frame_a indexed ['r1','r2'] and frame_b indexed ['r2','r3']; "
        "pd.concat([frame_a, frame_b], axis=1); assert shape (3,2) and exactly which "
        "cells are NaN (r1's y, r3's x)"
    )


# --------------------------------------------------------------------------
# EXERCISE 8 -- melt then pivot round trip. See starter/00_brief.md
# exercise 8.
#
# Check with:   pytest starter -v -k test_8
# --------------------------------------------------------------------------


def test_8_melt_then_pivot_round_trips_to_the_original(wide):
    pytest.skip(
        "exercise 8: melt wide on id_vars='student_id' to long form (assert shape "
        "(9,3)); pivot it back with index='student_id', columns='subject', "
        "values='score'; reset_index, drop the columns' name, reorder columns to "
        "match wide, and assert pd.testing.assert_frame_equal(recovered, wide)"
    )


# --------------------------------------------------------------------------
# EXERCISE 9 -- pivot versus pivot_table. See starter/00_brief.md
# exercise 9.
#
# Check with:   pytest starter -v -k test_9
# --------------------------------------------------------------------------


def test_9_pivot_raises_on_duplicate_index_column_pairs(dup_index_col):
    pytest.skip(
        "exercise 9a: dup_index_col.pivot(index='student', columns='subject', "
        "values='score') must raise ValueError -- ('Ann','math') appears twice"
    )


def test_9_pivot_table_aggregates_the_duplicates(dup_index_col):
    pytest.skip(
        "exercise 9b: dup_index_col.pivot_table(index='student', columns='subject', "
        "values='score', aggfunc='mean') must return Ann/math = 85.0 (mean of 80 and "
        "90), Ann/reading = 91.0, Bo/math = 70.0"
    )
