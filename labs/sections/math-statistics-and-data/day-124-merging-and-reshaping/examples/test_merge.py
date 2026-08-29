"""The worked reference suite for Day 124 -- "Joins That Keep Their Shape".

Nine exercises, each proving one real pandas 3.0.5 behaviour by running
code and reading real values -- never by reading source. Run it:

    pytest examples

Every table these tests use comes from `data.py`, imported through the
fixtures in `conftest.py`. Read `starter/00_brief.md` for the exercise-by-
exercise explanation; this file is the answer key.
"""

import numpy as np
import pandas as pd
import pytest

# --------------------------------------------------------------------------
# Exercise 1 -- the explosion. A many-to-many merge on duplicated keys
# produces exactly the product of the per-key group sizes, on each side,
# summed across keys. Not an error -- a Cartesian product within each key
# group, exactly as merge is defined to do.
# --------------------------------------------------------------------------


def test_1_many_to_many_merge_produces_the_per_key_product(left_dup, right_dup):
    assert left_dup.shape == (6, 3)
    assert right_dup.shape == (7, 3)

    merged = left_dup.merge(right_dup, on="cust_id", how="inner")

    # Compute the expected row count directly from the per-key group
    # sizes on each side -- the definition of what an inner merge does
    # with a duplicated key, not a number copied from a prior run.
    left_counts = left_dup["cust_id"].value_counts()
    right_counts = right_dup["cust_id"].value_counts()
    common_keys = set(left_counts.index) & set(right_counts.index)
    expected_rows = sum(left_counts[k] * right_counts[k] for k in common_keys)

    assert expected_rows == 14  # 3*2 (key A) + 2*4 (key B)
    assert merged.shape[0] == expected_rows
    assert merged.shape == (14, 5)  # cust_id + 2 left cols + 2 right cols

    # Per-key check: key A alone produces 3*2 = 6 rows.
    assert (merged["cust_id"] == "A").sum() == 6
    # Key B alone produces 2*4 = 8 rows.
    assert (merged["cust_id"] == "B").sum() == 8


# --------------------------------------------------------------------------
# Exercise 2 -- validate=. Stating a cardinality assumption and having
# pandas enforce it is the single best habit in this lesson.
# --------------------------------------------------------------------------


def test_2_validate_one_to_one_raises_on_duplicated_keys(left_dup, right_dup):
    with pytest.raises(pd.errors.MergeError):
        left_dup.merge(right_dup, on="cust_id", how="inner", validate="one_to_one")


def test_2_validate_one_to_one_passes_on_genuinely_unique_keys(left_keys, right_keys):
    # left_keys and right_keys each have a unique cust_id -- validate
    # should raise nothing at all, and the merge proceeds normally.
    result = left_keys.merge(right_keys, on="cust_id", how="inner", validate="one_to_one")
    assert result.shape == (3, 3)  # B, C, D


def test_2_validate_one_to_many_raises_when_the_many_side_is_actually_duplicated_on_both(left_dup, right_dup):
    # left_dup is NOT one-to-many against right_dup either: key A repeats
    # on BOTH sides (3 on the left, 2 on the right), so "one" (left) to
    # "many" (right) is violated on the left side too.
    with pytest.raises(pd.errors.MergeError):
        left_dup.merge(right_dup, on="cust_id", how="inner", validate="one_to_many")


# --------------------------------------------------------------------------
# Exercise 3 -- indicator=True. Adds a _merge column recording match
# provenance; the three counts must reconcile exactly with the inputs.
# --------------------------------------------------------------------------


def test_3_indicator_counts_reconcile_with_the_inputs(left_keys, right_keys):
    result = left_keys.merge(right_keys, on="cust_id", how="outer", indicator=True)

    counts = result["_merge"].value_counts()
    assert counts["left_only"] == 1  # A
    assert counts["right_only"] == 1  # E
    assert counts["both"] == 3  # B, C, D

    # Reconciliation: left_only + both accounts for every left row, since
    # every key on both sides here is unique (no duplication to explode).
    assert counts["left_only"] + counts["both"] == left_keys.shape[0] == 4
    assert counts["right_only"] + counts["both"] == right_keys.shape[0] == 4

    # And the three categories account for every output row exactly.
    assert counts["left_only"] + counts["right_only"] + counts["both"] == result.shape[0] == 5


# --------------------------------------------------------------------------
# Exercise 4 -- the silent dtype-mismatch join. An int64 key merged
# against a str key of the same digits matches nothing, and an inner join
# returns zero rows rather than raising.
# --------------------------------------------------------------------------


def test_4_dtype_mismatch_join_returns_zero_rows(int_keyed, str_keyed):
    assert int_keyed["id"].dtype == np.int64
    assert str(str_keyed["id"].dtype) == "category"

    result = int_keyed.merge(str_keyed, on="id", how="inner")

    assert result.shape[0] == 0  # no exception, no warning -- just nothing
    assert list(result.columns) == ["id", "name", "score"]


def test_4_casting_one_side_fixes_it(int_keyed, str_keyed):
    fixed = str_keyed.astype({"id": "int64"})
    result = int_keyed.merge(fixed, on="id", how="inner")

    assert result.shape[0] == 3
    assert result.loc[result["id"] == 1002, "score"].iloc[0] == 91


def test_4_plain_str_key_against_int64_raises_instead_of_matching_nothing(int_keyed):
    # An honest correction to the "always silent" story: pandas 3.0.5
    # checks a merge key's dtype compatibility BEFORE joining, and a
    # plain str (or legacy object) key against an int64 key raises a
    # clear ValueError rather than silently returning zero rows. The
    # categorical case above is the one that still slips through.
    plain_str_keyed = pd.DataFrame({"id": ["1001", "1002", "1003"], "score": [88, 91, 77]})
    assert str(plain_str_keyed["id"].dtype) == "str"

    with pytest.raises(ValueError, match="You are trying to merge on"):
        int_keyed.merge(plain_str_keyed, on="id", how="inner")


# --------------------------------------------------------------------------
# Exercise 5 -- the four join types on one pair of frames, so the
# differences are visible at a glance. left_keys: A, B, C, D. right_keys:
# B, C, D, E. Overlap: B, C, D.
# --------------------------------------------------------------------------


def test_5_inner_keeps_only_the_overlap(left_keys, right_keys):
    result = left_keys.merge(right_keys, on="cust_id", how="inner")
    assert result.shape[0] == 3
    assert set(result["cust_id"]) == {"B", "C", "D"}


def test_5_left_keeps_every_left_row(left_keys, right_keys):
    result = left_keys.merge(right_keys, on="cust_id", how="left")
    assert result.shape[0] == 4
    assert set(result["cust_id"]) == {"A", "B", "C", "D"}
    assert result.loc[result["cust_id"] == "A", "plan"].isna().all()


def test_5_right_keeps_every_right_row(left_keys, right_keys):
    result = left_keys.merge(right_keys, on="cust_id", how="right")
    assert result.shape[0] == 4
    assert set(result["cust_id"]) == {"B", "C", "D", "E"}
    assert result.loc[result["cust_id"] == "E", "region"].isna().all()


def test_5_outer_keeps_every_row_from_both(left_keys, right_keys):
    result = left_keys.merge(right_keys, on="cust_id", how="outer")
    assert result.shape[0] == 5
    assert set(result["cust_id"]) == {"A", "B", "C", "D", "E"}


def test_5_row_counts_in_one_table(left_keys, right_keys):
    counts = {
        how: left_keys.merge(right_keys, on="cust_id", how=how).shape[0]
        for how in ("inner", "left", "right", "outer")
    }
    assert counts == {"inner": 3, "left": 4, "right": 4, "outer": 5}


# --------------------------------------------------------------------------
# Exercise 6 -- suffixes. The default _x/_y on overlapping non-key
# columns is how price_x ends up in production; explicit suffixes fix it.
# --------------------------------------------------------------------------


def test_6_default_suffixes_are_x_and_y(price_left, price_right):
    result = price_left.merge(price_right, on="sku", how="inner")
    assert "price_x" in result.columns
    assert "price_y" in result.columns
    assert "price" not in result.columns
    assert result.loc[result["sku"] == "X1", "price_x"].iloc[0] == 9.99
    assert result.loc[result["sku"] == "X1", "price_y"].iloc[0] == 10.99


def test_6_explicit_suffixes_rename_as_asked(price_left, price_right):
    result = price_left.merge(price_right, on="sku", how="inner", suffixes=("_catalog", "_live"))
    assert "price_catalog" in result.columns
    assert "price_live" in result.columns
    assert "price_x" not in result.columns
    assert result.loc[result["sku"] == "X2", "price_catalog"].iloc[0] == 14.50
    assert result.loc[result["sku"] == "X2", "price_live"].iloc[0] == 13.00


def test_6_on_versus_left_on_right_on_give_the_same_result(price_left, price_right):
    renamed_right = price_right.rename(columns={"sku": "sku_code"})
    via_on = price_left.merge(price_right, on="sku", how="inner", suffixes=("_l", "_r"))
    via_left_right_on = price_left.merge(
        renamed_right, left_on="sku", right_on="sku_code", how="inner", suffixes=("_l", "_r")
    )
    assert via_on.shape[0] == via_left_right_on.shape[0] == 3
    assert list(via_on["price_l"]) == list(via_left_right_on["price_l"])


def test_6_join_on_index_matches_merge_on_column(price_left, price_right):
    left_indexed = price_left.set_index("sku")
    right_indexed = price_right.set_index("sku")

    via_join = left_indexed.join(right_indexed, how="inner", lsuffix="_l", rsuffix="_r")
    via_merge = price_left.merge(price_right, on="sku", how="inner", suffixes=("_l", "_r")).set_index("sku")

    assert via_join.sort_index().equals(via_merge.sort_index())


# --------------------------------------------------------------------------
# Exercise 7 -- concat. axis=0 stacks rows; axis=1 stacks columns.
# Alignment fills unmatched columns or labels with NaN rather than
# erroring.
# --------------------------------------------------------------------------


def test_7_concat_axis_0_with_mismatched_columns_fills_nan():
    frame_a = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    frame_b = pd.DataFrame({"b": [5, 6], "c": [7, 8]})

    result = pd.concat([frame_a, frame_b], axis=0, ignore_index=True)

    assert result.shape == (4, 3)
    assert list(result.columns) == ["a", "b", "c"]

    # frame_a's rows (0, 1) have no 'c' -- must be NaN there.
    assert result.loc[0:1, "c"].isna().all()
    # frame_b's rows (2, 3) have no 'a' -- must be NaN there.
    assert result.loc[2:3, "a"].isna().all()
    # 'b' is present in both, so it is never NaN here.
    assert not result["b"].isna().any()
    assert list(result["b"]) == [3, 4, 5, 6]


def test_7_concat_axis_1_with_mismatched_index_fills_nan():
    frame_a = pd.DataFrame({"x": [10, 20]}, index=["r1", "r2"])
    frame_b = pd.DataFrame({"y": [30, 40]}, index=["r2", "r3"])

    result = pd.concat([frame_a, frame_b], axis=1)

    assert result.shape == (3, 2)
    assert result.loc["r1", "y"] != result.loc["r1", "y"]  # NaN != NaN
    assert pd.isna(result.loc["r1", "y"])
    assert pd.isna(result.loc["r3", "x"])
    assert result.loc["r2", "x"] == 20
    assert result.loc["r2", "y"] == 30


# --------------------------------------------------------------------------
# Exercise 8 -- melt to go long, pivot to come back. The round trip must
# recover the original.
# --------------------------------------------------------------------------


def test_8_melt_then_pivot_round_trips_to_the_original(wide):
    long = wide.melt(id_vars="student_id", var_name="subject", value_name="score")

    assert long.shape == (9, 3)  # 3 students x 3 subjects
    assert set(long["subject"]) == {"math", "reading", "science"}

    recovered = (
        long.pivot(index="student_id", columns="subject", values="score")
        .reset_index()
        .rename_axis(columns=None)
    )
    # pivot sorts columns alphabetically -- put the original column order back.
    recovered = recovered[["student_id", "math", "reading", "science"]]

    pd.testing.assert_frame_equal(recovered, wide, check_dtype=True)


# --------------------------------------------------------------------------
# Exercise 9 -- pivot raises on duplicate index/column pairs; pivot_table
# aggregates them instead.
# --------------------------------------------------------------------------


def test_9_pivot_raises_on_duplicate_index_column_pairs(dup_index_col):
    # ("Ann", "math") appears twice -- pivot has nowhere to put both.
    with pytest.raises(ValueError):
        dup_index_col.pivot(index="student", columns="subject", values="score")


def test_9_pivot_table_aggregates_the_duplicates(dup_index_col):
    result = dup_index_col.pivot_table(index="student", columns="subject", values="score", aggfunc="mean")

    # Ann's two math scores, 80.0 and 90.0, average to 85.0.
    assert result.loc["Ann", "math"] == 85.0
    assert result.loc["Ann", "reading"] == 91.0
    assert result.loc["Bo", "math"] == 70.0
