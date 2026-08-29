"""YOUR test suite for Day 123 -- "Groups That Reconcile". Nine exercises.

Run it from the lab directory, not from here:

    pytest starter -v

Every exercise below ends in a `pytest.skip(...)` line. pytest reports a
skip as `s` in the dot line and moves on, so an unfinished suite still
exits 0. Replace each skip with real assertions -- deleting the skip line
is part of the exercise. `starter/00_brief.md` explains each exercise in
full; the fixtures you need (`orders`, `sales`, `cat_sales`, `weighted`,
`large`) come from `conftest.py` and are described there too.

Assert exact values everywhere except exercise 8's timing ratio, which is
inherently one machine on one day.
"""

import time

import numpy as np
import pandas as pd
import pytest

# --------------------------------------------------------------------------
# EXERCISE 1 -- the reconciliation invariant. groupby drops rows whose key
# is missing, by default, silently. See starter/00_brief.md exercise 1.
#
# Check with:   pytest starter -v -k test_1
# --------------------------------------------------------------------------


def test_1_dropna_true_undercounts_by_exactly_the_missing_rows(orders):
    pytest.skip(
        "exercise 1a: assert grouped_total (1945.0), overall_total (2115.0), "
        "the gap (170.0), and that the gap equals the missing-key rows' amount total exactly"
    )


def test_1_dropna_false_reconciles_exactly(orders):
    pytest.skip(
        "exercise 1b: with dropna=False, assert the NaN group's total is 170.0 "
        "and that the grouped sum equals orders['amount'].sum() exactly"
    )


# --------------------------------------------------------------------------
# EXERCISE 2 -- count() versus size(). size() counts rows; count() counts
# non-missing values per column.
#
# Check with:   pytest starter -v -k test_2
# --------------------------------------------------------------------------


def test_2_size_and_count_disagree_where_amount_is_missing(orders):
    pytest.skip(
        "exercise 2: group orders by region with dropna=False; assert size and "
        "count disagree on South and West, and that (size - count).sum() equals "
        "orders['amount'].isna().sum() exactly"
    )


# --------------------------------------------------------------------------
# EXERCISE 3 -- .agg() four ways: single function, list, per-column dict,
# and named aggregation.
#
# Check with:   pytest starter -v -k test_3
# --------------------------------------------------------------------------


def test_3_agg_single_function(sales):
    pytest.skip("exercise 3a: sales.groupby('region')['amount'].agg('sum'); assert East is 1080.0")


def test_3_agg_list_of_functions(sales):
    pytest.skip(
        "exercise 3b: .agg(['sum', 'mean', 'count']); assert the column names "
        "and East's three values"
    )


def test_3_agg_per_column_dict(sales):
    pytest.skip(
        "exercise 3c: .agg({'amount': 'sum', 'order_id': 'count'}); assert "
        "North's amount sum and order_id count"
    )


def test_3_agg_named_aggregation_gives_flat_columns(sales):
    pytest.skip(
        "exercise 3d: .agg(total=('amount','sum'), avg=('amount','mean'), "
        "n=('order_id','count')); assert the result columns are flat, NOT a "
        "MultiIndex, and check West's three values"
    )


# --------------------------------------------------------------------------
# EXERCISE 4 -- agg reduces each group to one row; transform returns the
# input's shape. Use transform to build a within-group z-score.
#
# Check with:   pytest starter -v -k test_4
# --------------------------------------------------------------------------


def test_4_agg_returns_one_row_per_group(sales):
    pytest.skip("exercise 4a: assert sales.groupby('region')['amount'].agg('mean').shape == (4,)")


def test_4_transform_returns_the_input_shape(sales):
    pytest.skip(
        "exercise 4b: assert sales.groupby('region')['amount'].transform('mean').shape "
        "matches sales.shape[0], not the number of groups"
    )


def test_4_transform_attaches_a_group_mean_to_every_row(sales):
    pytest.skip(
        "exercise 4c: assert every North row's transformed group mean equals 120.0"
    )


def test_4_within_group_zscore_has_zero_mean_per_group(sales):
    pytest.skip(
        "exercise 4d: build (amount - group_mean) / group_std using transform for "
        "both, then assert each region's z-scores average to 0 within pytest.approx"
    )


# --------------------------------------------------------------------------
# EXERCISE 5 -- GroupBy.filter keeps or drops WHOLE GROUPS by a predicate.
# Distinct from Day 122's row-level filtering.
#
# Check with:   pytest starter -v -k test_5
# --------------------------------------------------------------------------


def test_5_filter_drops_whole_groups_below_the_threshold(orders):
    pytest.skip(
        "exercise 5: filter orders.groupby('region') to groups of size >= 3; "
        "assert West is entirely absent from the survivors and that the survivors' "
        "row count equals the sum of the surviving groups' own sizes (9)"
    )


# --------------------------------------------------------------------------
# EXERCISE 6 -- multi-key grouping produces a MultiIndex; as_index=False
# gives a flat frame with the same values.
#
# Check with:   pytest starter -v -k test_6
# --------------------------------------------------------------------------


def test_6_multi_key_grouping_produces_a_multiindex(sales):
    pytest.skip(
        "exercise 6a: group sales by ['region', 'rep'], assert the result index "
        "is a pandas.MultiIndex with names ['region', 'rep'], and check "
        "('East', 'Ann') is 420.0"
    )


def test_6_as_index_false_gives_the_same_values_flat(sales):
    pytest.skip(
        "exercise 6b: repeat with as_index=False; assert the result is NOT a "
        "MultiIndex and that ('East', 'Ann')'s value still matches exercise 6a"
    )


# --------------------------------------------------------------------------
# EXERCISE 7 -- observed=. Grouping a categorical produces rows for every
# possible combination unless observed=True.
#
# Check with:   pytest starter -v -k test_7
# --------------------------------------------------------------------------


def test_7_observed_false_manufactures_unseen_combinations(cat_sales):
    pytest.skip(
        "exercise 7a: group cat_sales by ['region', 'rep'] with observed=False; "
        "assert the result has 20 rows (5 region categories x 4 rep categories)"
    )


def test_7_observed_true_keeps_only_combinations_actually_seen(cat_sales):
    pytest.skip(
        "exercise 7b: repeat with observed=True; assert the result has 9 rows "
        "and that ('North', 'Ann') is 2"
    )


# --------------------------------------------------------------------------
# EXERCISE 8 -- performance. Report the SHAPE of the gap, never a
# millisecond figure.
#
# Check with:   pytest starter -v -k test_8
# --------------------------------------------------------------------------


def test_8_builtin_agg_beats_apply_by_a_wide_margin(large):
    pytest.skip(
        "exercise 8a: time large.groupby('key')['value'].agg('mean') against "
        "large.groupby('key')['value'].apply(lambda g: g.mean()); assert both give "
        "the same numbers, then assert apply_seconds / builtin_seconds >= 3.0"
    )


def test_8_sort_false_does_not_change_the_values(large):
    pytest.skip(
        "exercise 8b: assert groupby(sort=True) and groupby(sort=False) give the "
        "same values once both are sorted for comparison"
    )


# --------------------------------------------------------------------------
# EXERCISE 9 -- a weighted mean per group, computed with apply and again
# without it, asserting the two agree.
#
# Check with:   pytest starter -v -k test_9
# --------------------------------------------------------------------------


def test_9_weighted_mean_via_apply(weighted):
    pytest.skip(
        "exercise 9a: write a weighted_mean(group) function using "
        "np.average(group['value'], weights=group['weight']); apply it per region "
        "with include_groups=False; assert North is approx(17.5), South approx(13.0), "
        "East approx(60.0)"
    )


def test_9_weighted_mean_without_apply_agrees(weighted):
    pytest.skip(
        "exercise 9b: compute the same weighted means WITHOUT apply -- build a "
        "value*weight column, sum both columns per group with .agg, then divide -- "
        "and assert the result equals exercise 9a's result exactly"
    )
