"""The reference answers for Day 137 -- "Features That Do Not Cheat".

Nine exercises, each one a measurement rather than an opinion. Read
`starter/test_features.py` and try them yourself before reading this.

Every band in here was chosen after running the experiment, not before,
and the bands are wide enough to describe the result honestly rather than
narrow enough to look impressive. Where a number is exact arithmetic --
exercise 5 -- the assertion is exact.
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
    """A feature derived from the outcome scores perfectly. That is the bug."""
    assert leakage["with_leak"] >= 0.99, "the planted leak should be near-perfect"
    assert leakage["with_leak"] == 1.0

    # The honest band. Three weak behavioural features on a task with a
    # 44% base rate cannot do much better than this, and a result far
    # above it would itself be a reason to go looking for another leak.
    assert 0.55 <= leakage["without_leak"] <= 0.80
    assert leakage["gap_points"] >= 25.0

    # And the reason the leak is a leak: the column does not exist until
    # after the outcome it is predicting.
    frame = data.signups()
    unconverted = frame.loc[frame["converted"] == 0, "days_to_first_invoice"]
    converted = frame.loc[frame["converted"] == 1, "days_to_first_invoice"]
    assert set(unconverted.unique()) == {-1.0}
    assert converted.min() >= 1.0


# --- 2 ---------------------------------------------------------------------


def test_fitting_before_the_split_costs_nothing_for_a_scaler_and_a_lot_for_an_imputer(
    scaler_contamination, imputer_contamination
):
    """Contamination is only worth what the contaminated statistic is worth.

    The scaler result is the surprise, and it is measured over 200
    splits rather than argued: standardisation applies ONE affine map to
    both halves, so contaminating it can only change the relative
    weighting of the features, and that is worth almost nothing here.
    The group-mean imputer is not affine -- it fills each gap from its
    own group -- and contaminating it is worth several points.
    """
    assert scaler_contamination["trials"] == 200
    assert abs(scaler_contamination["optimism_points"]) < 1.0

    assert imputer_contamination["contaminated"] > imputer_contamination["correct"]
    assert imputer_contamination["optimism_points"] >= 5.0
    assert imputer_contamination["test_size"] == 200

    # The scaler really was contaminated -- its statistics differ plainly.
    # The score did not move; the numbers did.
    frame = data.pricing()
    X = frame[["order_value", "tenure_days"]].to_numpy(dtype=float)
    train_idx, _ = M.random_split(len(frame), 25, 137)
    everything = F.Standardiser().fit(X)
    train_only = F.Standardiser().fit(X[train_idx[:60]])
    assert abs(everything.mean_[0] - train_only.mean_[0]) > 5.0


# --- 3 ---------------------------------------------------------------------


def test_target_encoding_leaks_when_it_is_fitted_before_the_split(encoding):
    """Replace a category with the mean outcome and you have used the target."""
    assert encoding["naive_all_data"] > encoding["out_of_fold"]
    assert encoding["gap_all_vs_oof_points"] >= 4.0

    # Restricting the encoding to the training rows removes the whole
    # inflation. Out-of-fold then buys a little more on top, because a
    # training row's own target no longer feeds its own feature.
    assert encoding["out_of_fold"] >= encoding["naive_train_only"]
    assert encoding["naive_all_data"] - encoding["naive_train_only"] >= 0.04

    # The direct evidence, without a model in the way: the naive encoding
    # is far more correlated with the target than the honest one, and the
    # difference is the part it copied from the answer.
    frame = data.city_signups()
    city = frame["city"].to_numpy()
    y = frame["converted"].to_numpy()
    mapping, default = F.target_encode_fit(city, y)
    naive = F.target_encode_transform(city, mapping, default)
    out_of_fold = F.target_encode_out_of_fold(city, y, n_folds=5, seed=137)
    assert float(np.corrcoef(naive, y)[0, 1]) > 0.25
    assert float(np.corrcoef(out_of_fold, y)[0, 1]) < 0.10


# --- 4 ---------------------------------------------------------------------


def test_a_random_split_hides_what_a_time_ordered_split_shows(temporal):
    """The number you can trust is the smaller one."""
    assert temporal["random_split"] >= 0.80
    assert temporal["time_ordered_split"] <= 0.20
    assert temporal["gap_points"] >= 50.0

    # The mechanism, stated as an assertion: the time-ordered training
    # rows never contain the final batch, and the random ones contain
    # every batch there is.
    assert temporal["batches_seen_by_random_train"] == 6.0
    assert temporal["batches_seen_by_ordered_train"] == 5.0
    assert temporal["test_batches_unseen_by_ordered_train"] == 1.0

    # Worse than uninformed: the model is confidently wrong, scoring far
    # below the majority-class baseline for that period.
    assert temporal["time_ordered_split"] < temporal["majority_rate_in_ordered_test"]


# --- 5 ---------------------------------------------------------------------


def test_cyclical_encoding_restores_the_adjacency_of_hour_23_and_hour_0(cyclical):
    """Exact arithmetic, so these assertions are exact."""
    assert cyclical["raw_23_to_0"] == 23.0
    assert cyclical["raw_3_to_4"] == 1.0
    assert cyclical["raw_adjacent_spread"] == 22.0

    expected = 2.0 * math.sin(math.pi / 24.0)
    assert cyclical["cyclical_23_to_0"] == pytest.approx(expected, abs=1e-12)
    assert cyclical["cyclical_3_to_4"] == pytest.approx(expected, abs=1e-12)
    assert cyclical["cyclical_adjacent_spread"] < 1e-12

    # Opposite hours stay opposite: the circle has diameter 2.
    assert cyclical["cyclical_0_to_12"] == pytest.approx(2.0, abs=1e-12)

    # Every one of the 24 adjacent pairs, wrap included, is the same
    # distance apart -- which is the property the raw integer lacks.
    circle = F.cyclical_encode(np.arange(24), 24)
    distances = [
        float(np.linalg.norm(circle[h] - circle[(h + 1) % 24])) for h in range(24)
    ]
    assert max(distances) - min(distances) < 1e-12


# --- 6 ---------------------------------------------------------------------


def test_an_ordinal_code_forces_an_order_that_one_hot_does_not(colours):
    """Six colours, no order, and a model that has to invent one."""
    assert colours["ordinal_is_monotone"] is True
    assert colours["one_hot_is_monotone"] is False

    # One-hot reproduces each colour's observed rate essentially exactly.
    assert colours["one_hot_max_error"] < 1e-5
    assert colours["one_hot_predictions"] == pytest.approx(
        colours["observed_rates"], abs=1e-5
    )

    # The ordinal model cannot: it is out by more than a third somewhere.
    assert colours["ordinal_max_error"] > 0.30
    assert colours["ordinal_accuracy"] < colours["one_hot_accuracy"]

    # And the reason: the true rates are not monotone in the code.
    observed = colours["observed_rates"]
    assert observed[2] > observed[1]
    assert observed[3] < observed[2]


# --- 7 ---------------------------------------------------------------------


def test_a_ratio_separates_what_neither_column_separates(interaction):
    """Spend and income overlap. Spend over income does not."""
    assert interaction["ratio_only"] == 1.0
    assert interaction["income_only"] < 0.60
    assert interaction["spend_only"] < 0.75
    assert interaction["ratio_only"] - max(
        interaction["income_only"], interaction["spend_only"]
    ) >= 0.25

    # Honest footnote, asserted rather than hidden: because the boundary
    # here is a straight line through the origin, a linear model given
    # both raw columns can reach the same score. The ratio is still the
    # feature that makes the rule visible, and a distance-based model
    # gets nothing from the two raw columns.
    assert interaction["income_and_spend"] >= 0.95


# --- 8 ---------------------------------------------------------------------


def test_the_vocabulary_must_be_chosen_on_training_documents_only(vocabulary):
    """Which words become features is itself a fitted statistic."""
    assert vocabulary["fitted_on_all_data"] > vocabulary["fitted_on_train_only"]
    assert vocabulary["gap_points"] >= 1.5
    assert vocabulary["trials"] == 40

    # Unseen words are handled, not crashed on: the matrix keeps exactly
    # the training vocabulary's width and the test-only tokens are simply
    # not counted.
    assert vocabulary["unseen_test_words"] > 0
    assert vocabulary["test_matrix_columns"] == vocabulary["top_k"]
    assert vocabulary["test_matrix_rows"] == 100.0

    # Transforming a document made only of words the vocabulary has never
    # seen gives a row of zeros rather than an exception.
    trained = F.Vocabulary(top_k=5, min_docs=1).fit(
        ["outage refund now", "thanks hello there"], np.array([1, 0])
    )
    matrix = trained.transform(["quetzal marzipan"])
    assert matrix.shape == (1, len(trained.words))
    assert matrix.sum() == 0.0


# --- 9 ---------------------------------------------------------------------


def test_the_audit_catches_the_planted_leaks_and_leaves_honest_columns_alone(audit):
    """A reusable check, and an honest account of what it cannot see."""
    assert audit["flagged"] == ["days_to_first_invoice", "email_template"]
    assert audit["rules"]["days_to_first_invoice"] == "separable"
    assert audit["rules"]["email_template"] == "pure_category"

    for honest in ("visits", "minutes_on_site", "discount_pct", "channel"):
        assert honest in audit["columns_checked"]
        assert honest not in audit["flagged"]

    # The correlation rule alone would have missed the numeric leak: its
    # absolute correlation with the target is 0.85, under the 0.90
    # threshold. The separability rule is what earns its place.
    frame = E.audit_table()
    y = frame["converted"].to_numpy(dtype=float)
    leak = frame["days_to_first_invoice"].to_numpy(dtype=float)
    correlation = abs(float(np.corrcoef(leak, y)[0, 1]))
    assert 0.80 < correlation < 0.90
    assert F.leakage_audit(frame, "converted", corr_threshold=0.99) != []

    # Raising the threshold above 1 disables the correlation rule
    # entirely, and the separability rule still catches it.
    strict = F.leakage_audit(frame, "converted", corr_threshold=1.01)
    assert [f.column for f in strict] == ["days_to_first_invoice", "email_template"]
