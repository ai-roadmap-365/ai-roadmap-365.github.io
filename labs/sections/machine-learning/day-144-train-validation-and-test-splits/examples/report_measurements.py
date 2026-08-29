#!/usr/bin/env python3
"""Print every measured pair in this lab as one table.

The harness compares this output byte for byte against
expected-output/measured-values.txt, so the report is not a convenience:
it is how the lab notices that a number in the lesson has gone stale.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402

import splits_lib as s  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 144 -- train, validation and test splits, measured")
    print("=" * 53)

    rule("1. Why three sets: selecting on a set is fitting to it")
    standard_error = s.proportion_standard_error(0.5, 500)
    print("  K candidates, each a coin flip, 500-row validation and 500-row test")
    print(f"  averaged over 400 replications; standard error of an accuracy is {standard_error:.4f}")
    print("     K   best-val   its-test   optimism   in SEs")
    rows = s.selection_bias_curve([1, 2, 5, 10, 25, 50, 100, 500, 1000])
    for k, validation, test, optimism in rows:
        print(f"  {k:5d}    {validation:.4f}     {test:.4f}    {optimism:+.4f}    {optimism / standard_error:5.2f}")
    print("  the test column never moves: it was never selected on")

    rule("1b. The optimism is the expected maximum of K noise draws")
    print("     K   measured   E max of K normals   sqrt(2 ln K)")
    for k, _v, _t, optimism in rows[1:]:
        print(
            f"  {k:5d}     {optimism / standard_error:5.2f}              "
            f"{s.expected_max_of_normals(k):5.2f}          {s.sqrt_two_log_k(k):5.2f}"
        )
    print("  the closed-form approximation sits above the truth at every K here")

    rule("2. Stratification: a rare class and a small test set")
    X, y = s.rare_class_dataset()
    random_rates, stratified_rates, empty = s.split_positive_rates(X, y)
    print(f"  population positive rate : {float(y.mean()):.4f}")
    print(f"  random split     : {s.spread(random_rates)}")
    print(f"  stratified split : {s.spread(stratified_rates)}")
    print(f"  random splits whose test half held ZERO positives: {empty} of 500")

    rule("3. Groups: when the row is not the unit")
    Xg, yg, groups = s.grouped_dataset()
    rowwise, group_aware = s.rowwise_vs_group_split(Xg, yg, groups)
    print("  50 people, 20 rows each; each person's label is a coin flip")
    print(f"  row-wise random split : {rowwise:.4f}")
    print(f"  group-aware split     : {group_aware:.4f}")
    print(f"  accuracy invented     : {rowwise - group_aware:+.4f}")
    print(f"  people appearing in BOTH halves of a row-wise split: {s.groups_shared_between_halves(groups)} of 50")

    rule("4. Time: when the data has a direction")
    temporal = s.temporal_inflation_over_constructions()
    inflation = [gap for _s, _sh, _ch, _b, gap in temporal]
    print("  20 independently generated series, six regimes each")
    print(f"  shuffled split, mean       : {np.mean([r[1] for r in temporal]):.4f}")
    print(f"  chronological split, mean  : {np.mean([r[2] for r in temporal]):.4f}")
    print(f"  majority baseline, mean    : {np.mean([r[3] for r in temporal]):.4f}")
    print(f"  inflation: mean {np.mean(inflation):.4f}  sd {np.std(inflation):.4f}  "
          f"min {min(inflation):+.4f}  max {max(inflation):+.4f}")
    print(f"  constructions where shuffling won: {sum(1 for g in inflation if g > 0)} of 20")
    print("  the direction is universal; the size varies by a factor of sixteen")

    rule("5. One holdout, or many folds")
    Xw, yw = s.weak_signal_dataset()
    holdout, cross = s.holdout_vs_cross_validation(Xw, yw)
    print("  same data, same model; only which rows landed where changes")
    print(f"  single holdout : {s.spread(holdout)}")
    print(f"  5-fold         : {s.spread(cross)}")
    print(f"  holdout swings {max(holdout) - min(holdout):.4f} across 200 seeds")
    print(f"  cross-validation is {np.std(holdout) / np.std(cross):.4f} times steadier")

    rule("6. How big does the test set need to be?")
    print("       n   theory SE   measured sd   95 percent half-width")
    for n, theory, measured, half in s.test_size_table([50, 100, 200, 500, 1000, 5000]):
        print(f"  {n:6d}      {theory:.4f}        {measured:.4f}                 +/-{half:.4f}")
    print(f"  rows needed for +/-0.02 at an accuracy of 0.85 : {s.rows_needed_for_precision(0.85, 0.02)}")
    print(f"  rows needed for +/-0.01 at an accuracy of 0.85 : {s.rows_needed_for_precision(0.85, 0.01)}")

    rule("7. The rule, made mechanical")
    model = LogisticRegression(max_iter=1000).fit(Xw, yw)
    gate = s.GatedTestSet(Xw, yw)
    print(f"  first evaluation  : {gate.evaluate(model):.4f}")
    try:
        gate.evaluate(model)
        print("  second evaluation : NO ERROR RAISED")
    except s.TestSetTouchedTwice as exc:
        print(f"  second evaluation : {type(exc).__name__}")
        print(f"    {exc}")


if __name__ == "__main__":
    main()
