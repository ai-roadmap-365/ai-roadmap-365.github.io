"""The worked reference suite for Day 123 -- "Groups That Reconcile".

Nine exercises, each proving one real pandas 3.0.5 behaviour by running code
and reading real values -- never by reading source. Run it:

    pytest examples

Every table these tests use comes from `data.py`, imported through the
fixtures in `conftest.py`. Read `starter/00_brief.md` for the exercise-by-
exercise explanation; this file is the answer key.
"""

import time

import numpy as np
import pandas as pd
import pytest

# --------------------------------------------------------------------------
# Exercise 1 -- the reconciliation invariant
#
# groupby drops rows whose key is missing, by default, silently. Prove the
# gap exists, prove it equals exactly the missing-key rows' total, and prove
# dropna=False makes the parts sum back to the whole.
# --------------------------------------------------------------------------


def test_1_dropna_true_undercounts_by_exactly_the_missing_rows(orders):
    grouped_total = orders.groupby("region")["amount"].sum().sum()
    overall_total = orders["amount"].sum()
    gap = overall_total - grouped_total

    assert grouped_total == 1945.0
    assert overall_total == 2115.0
    assert gap == 170.0

    missing_key_total = orders.loc[orders["region"].isna(), "amount"].sum()
    assert missing_key_total == 170.0
    assert gap == missing_key_total, "the gap must equal exactly the missing-key rows' total"

    missing_key_count = orders["region"].isna().sum()
    assert missing_key_count == 2


def test_1_dropna_false_reconciles_exactly(orders):
    grouped = orders.groupby("region", dropna=False)["amount"].sum()

    # The NaN group is real and carries the missing rows' total.
    assert grouped.loc[np.nan] == 170.0

    # Now the parts add back up to the whole, to the last cent.
    assert grouped.sum() == orders["amount"].sum() == 2115.0


# --------------------------------------------------------------------------
# Exercise 2 -- count() versus size(). size() counts ROWS; count() counts
# NON-MISSING VALUES per column. They disagree exactly where data is
# missing, and confusing them misstates every denominator downstream.
# --------------------------------------------------------------------------


def test_2_size_and_count_disagree_where_amount_is_missing(orders):
    grouped = orders.groupby("region", dropna=False)
    size = grouped.size()
    count = grouped["amount"].count()

    assert size.loc["South"] == 3
    assert count.loc["South"] == 2  # one of South's three amounts is NaN

    assert size.loc["West"] == 1
    assert count.loc["West"] == 0  # West's only amount is NaN

    diff = size - count
    assert diff.sum() == 2
    assert diff.sum() == orders["amount"].isna().sum(), (
        "the total gap between size and count must equal the missing-amount count exactly"
    )


# --------------------------------------------------------------------------
# Exercise 3 -- .agg() four ways: one function, a list, a per-column dict,
# and named aggregation, which is the readable modern form and produces
# flat column names instead of a MultiIndex.
# --------------------------------------------------------------------------


def test_3_agg_single_function(sales):
    result = sales.groupby("region")["amount"].agg("sum")
    assert result.loc["East"] == 1080.0
    assert result.loc["North"] == 360.0
    assert result.loc["South"] == 600.0
    assert result.loc["West"] == 195.0


def test_3_agg_list_of_functions(sales):
    result = sales.groupby("region")["amount"].agg(["sum", "mean", "count"])
    assert list(result.columns) == ["sum", "mean", "count"]
    assert result.loc["East", "sum"] == 1080.0
    assert result.loc["East", "mean"] == pytest.approx(360.0)
    assert result.loc["East", "count"] == 3


def test_3_agg_per_column_dict(sales):
    result = sales.groupby("region").agg({"amount": "sum", "order_id": "count"})
    assert result.loc["North", "amount"] == 360.0
    assert result.loc["North", "order_id"] == 3


def test_3_agg_named_aggregation_gives_flat_columns(sales):
    result = sales.groupby("region").agg(
        total=("amount", "sum"), avg=("amount", "mean"), n=("order_id", "count")
    )
    # Flat column names, not a MultiIndex -- that is the whole point of
    # named aggregation over the list/dict forms above.
    assert list(result.columns) == ["total", "avg", "n"]
    assert not isinstance(result.columns, pd.MultiIndex)
    assert result.loc["West", "total"] == 195.0
    assert result.loc["West", "avg"] == pytest.approx(65.0)
    assert result.loc["West", "n"] == 3


# --------------------------------------------------------------------------
# Exercise 4 -- agg reduces each group to one row; transform returns the
# input's shape, which is how a group statistic gets attached back to
# every row (here: a within-group z-score whose group mean is 0).
# --------------------------------------------------------------------------


def test_4_agg_returns_one_row_per_group(sales):
    result = sales.groupby("region")["amount"].agg("mean")
    assert result.shape == (4,)  # four regions


def test_4_transform_returns_the_input_shape(sales):
    result = sales.groupby("region")["amount"].transform("mean")
    assert result.shape == (12,)  # twelve rows, same as sales itself
    assert result.shape[0] == sales.shape[0]


def test_4_transform_attaches_a_group_mean_to_every_row(sales):
    group_mean = sales.groupby("region")["amount"].transform("mean")
    # North's three amounts are 120, 80, 160 -- mean 120.
    north_rows = sales["region"] == "North"
    assert (group_mean[north_rows] == 120.0).all()


def test_4_within_group_zscore_has_zero_mean_per_group(sales):
    group_mean = sales.groupby("region")["amount"].transform("mean")
    group_std = sales.groupby("region")["amount"].transform("std")
    zscore = (sales["amount"] - group_mean) / group_std

    per_group_zscore_mean = zscore.groupby(sales["region"]).mean()
    for region, value in per_group_zscore_mean.items():
        assert value == pytest.approx(0.0, abs=1e-9), f"{region}'s z-scores must average to 0"


# --------------------------------------------------------------------------
# Exercise 5 -- GroupBy.filter keeps or discards WHOLE GROUPS by a
# predicate. Distinct from Day 122's row-level filtering, despite the
# shared word.
# --------------------------------------------------------------------------


def test_5_filter_drops_whole_groups_below_the_threshold(orders):
    sizes = orders.groupby("region").size()
    assert sizes.to_dict() == {"East": 3, "North": 3, "South": 3, "West": 1}

    survivors = orders.groupby("region").filter(lambda g: len(g) >= 3)

    # West (size 1) is dropped whole; nothing partial survives from it.
    assert "West" not in survivors["region"].unique()
    assert set(survivors["region"].unique()) == {"East", "North", "South"}

    # The row count matches the sum of the surviving groups' own sizes.
    assert survivors.shape[0] == sizes[sizes >= 3].sum() == 9


# --------------------------------------------------------------------------
# Exercise 6 -- multi-key grouping produces a MultiIndex; as_index=False
# gives a flat frame with the same values.
# --------------------------------------------------------------------------


def test_6_multi_key_grouping_produces_a_multiindex(sales):
    result = sales.groupby(["region", "rep"])["amount"].sum()
    assert isinstance(result.index, pd.MultiIndex)
    assert result.index.names == ["region", "rep"]
    assert result.loc[("East", "Ann")] == 420.0
    assert result.loc[("West", "Cy")] == 45.0


def test_6_as_index_false_gives_the_same_values_flat(sales):
    indexed = sales.groupby(["region", "rep"])["amount"].sum()
    flat = sales.groupby(["region", "rep"], as_index=False)["amount"].sum()

    assert not isinstance(flat.index, pd.MultiIndex)
    assert list(flat.columns) == ["region", "rep", "amount"]

    east_ann = flat.loc[(flat["region"] == "East") & (flat["rep"] == "Ann"), "amount"].iloc[0]
    assert east_ann == indexed.loc[("East", "Ann")] == 420.0


# --------------------------------------------------------------------------
# Exercise 7 -- observed=. Grouping a categorical produces rows for
# unobserved combinations unless observed=True. With two categorical keys
# this explodes combinatorially.
# --------------------------------------------------------------------------


def test_7_observed_false_manufactures_unseen_combinations(cat_sales):
    # 5 region categories x 4 rep categories = 20 possible combinations,
    # only 9 of which are ever actually seen in the 12 rows of data.
    result = cat_sales.groupby(["region", "rep"], observed=False).size()
    assert len(result) == 20


def test_7_observed_true_keeps_only_combinations_actually_seen(cat_sales):
    result = cat_sales.groupby(["region", "rep"], observed=True).size()
    assert len(result) == 9
    assert result.loc[("North", "Ann")] == 2


# --------------------------------------------------------------------------
# Exercise 8 -- performance. Report the SHAPE of the gap between a
# built-in aggregation and the equivalent .apply(lambda ...), not a
# millisecond figure -- this is one machine, one day.
# --------------------------------------------------------------------------


def test_8_builtin_agg_beats_apply_by_a_wide_margin(large):
    start = time.perf_counter()
    builtin_result = large.groupby("key")["value"].agg("mean")
    builtin_seconds = time.perf_counter() - start

    start = time.perf_counter()
    apply_result = large.groupby("key")["value"].apply(lambda g: g.mean())
    apply_seconds = time.perf_counter() - start

    # Both paths must agree on the actual numbers -- speed is not the
    # only thing being asserted here.
    assert np.allclose(builtin_result.sort_index().to_numpy(), apply_result.sort_index().to_numpy())

    # The margin is asserted as a conservative ratio, never a timing.
    # This machine measured roughly 10-15x; 3x is asserted as the floor
    # so the check does not flake on a slower or busier machine.
    ratio = apply_seconds / builtin_seconds
    assert ratio >= 3.0, f"expected .apply to be at least 3x slower, measured {ratio:.1f}x"


def test_8_sort_false_does_not_change_the_values(large):
    sorted_result = large.groupby("key", sort=True)["value"].sum()
    unsorted_result = large.groupby("key", sort=False)["value"].sum()
    assert sorted_result.sort_index().equals(unsorted_result.sort_index())
    # sort=False is not guaranteed to change ORDER on every input, but it
    # must never change the VALUES -- that is the only thing asserted here.


# --------------------------------------------------------------------------
# Exercise 9 -- a weighted mean per group, computed with apply and again
# without it, asserting the two agree.
# --------------------------------------------------------------------------


def test_9_weighted_mean_via_apply(weighted):
    def weighted_mean(group: pd.DataFrame) -> float:
        return float(np.average(group["value"], weights=group["weight"]))

    via_apply = weighted.groupby("region").apply(weighted_mean, include_groups=False)

    assert via_apply.loc["North"] == pytest.approx(17.5)  # (10*1 + 20*3) / 4
    assert via_apply.loc["South"] == pytest.approx(13.0)  # (5*2+15*2+25*1) / 5
    assert via_apply.loc["East"] == pytest.approx(60.0)  # (100*1 + 50*4) / 5


def test_9_weighted_mean_without_apply_agrees(weighted):
    def weighted_mean(group: pd.DataFrame) -> float:
        return float(np.average(group["value"], weights=group["weight"]))

    via_apply = weighted.groupby("region").apply(weighted_mean, include_groups=False)

    # The vectorised route: build a value*weight column, sum both pieces
    # per group with .agg, then divide -- no apply anywhere.
    weighted_products = weighted.assign(value_weight=weighted["value"] * weighted["weight"])
    sums = weighted_products.groupby("region").agg(
        sum_value_weight=("value_weight", "sum"), sum_weight=("weight", "sum")
    )
    without_apply = sums["sum_value_weight"] / sums["sum_weight"]

    assert without_apply.sort_index().equals(via_apply.sort_index())
