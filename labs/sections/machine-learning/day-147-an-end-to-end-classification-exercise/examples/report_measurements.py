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

import classification_lib as c  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 147 -- an end-to-end classification exercise, measured")
    print("=" * 59)

    rule("1. Choosing the dataset, by measuring")
    print("  name            n_samples  n_features  n_classes  baseline  n_test")
    for name, n_samples, n_features, n_classes, baseline, n_test in c.candidate_summaries():
        print(f"  {name:14s}  {n_samples:9d}  {n_features:10d}  {n_classes:9d}  {baseline:.4f}    {n_test:4d}")
    print("  iris and wine saturate near-perfect accuracy on 30-36 test rows;")
    print("  breast_cancer is chosen: a non-trivial baseline, 114 test rows, room for an interval")

    X, y, names = c.load_chosen_dataset()
    x_train, x_test, y_train, y_test = c.split_once(X, y, seed=0)
    print(f"  chosen: breast_cancer, {X.shape[0]} rows, {X.shape[1]} features, classes {names}")
    print(f"  split: train={x_train.shape[0]}  test={x_test.shape[0]}  (stratified, seed 0)")

    rule("2. The frame and the baseline")
    baseline_acc = c.majority_baseline(x_train, y_train, x_test, y_test)
    print(f"  majority-class baseline, test accuracy: {baseline_acc:.4f}")

    rule("3. The sweep: cross-validate every candidate on train rows only")
    k = c.candidate_count()
    print(f"  K = {k} candidate pipelines: 15 KNN, 11 logistic regression, 10 decision trees")
    family, param, cv_mean, fitted = c.select_best(x_train, y_train, seed=0)
    print(f"  winner: {family} ({param})  5-fold CV accuracy = {cv_mean:.4f}")

    rule("4. ONE test evaluation")
    gate = c.GatedTestSet(x_test, y_test)
    test_acc = gate.evaluate(fitted)
    drop = round(cv_mean - test_acc, 4)
    print(f"  test accuracy: {test_acc:.4f}")
    print(f"  cv - test (the drop): {drop:+.4f}")
    try:
        gate.evaluate(fitted)
        print("  second evaluation: NO ERROR RAISED")
    except c.TestSetTouchedTwice as exc:
        print(f"  second evaluation : {type(exc).__name__}")
        print(f"    {exc}")

    rule("5. The predicted optimism, from Day 144's formula")
    predicted = round(c.predicted_selection_optimism(cv_mean, len(y_train), k), 4)
    print(f"  predicted optimism (SE of a CV fold x expected max of {k} normals): {predicted:.4f}")
    print(f"  measured drop at this seed: {drop:+.4f}")
    print("  one seed is an anecdote -- the distribution below is the honest reading")

    rule("5b. Predicted vs measured, over 20 seeds")
    rows = c.selection_optimism_over_seeds(X, y, seeds=range(20))
    drops = np.array([r[3] for r in rows])
    predicted_all = np.array([r[4] for r in rows])
    print("   seed   cv_mean   test_acc     drop   predicted")
    for seed, cv_mean_s, test_acc_s, drop_s, predicted_s in rows:
        print(f"  {seed:5d}   {cv_mean_s:.4f}    {test_acc_s:.4f}   {drop_s:+.4f}     {predicted_s:.4f}")
    print(f"  mean measured drop: {float(drops.mean()):+.4f}  sd {float(drops.std()):.4f}")
    print(f"  mean predicted optimism: {float(predicted_all.mean()):.4f}")
    print(f"  fraction of seeds where the drop was positive: {float((drops > 0).mean()):.4f}")
    print("  the formula assumed independent, zero-skill candidates; these 36 are correlated")
    print("  and genuinely skilled, so the naive prediction overestimates the real optimism here")

    rule("6. Error analysis")
    preds = fitted.predict(x_test)
    matrix, false_negatives, false_positives = c.confusion_and_errors(y_test, preds, names)
    print(f"  confusion matrix (rows=true, cols=predicted), labels {names}")
    for row in matrix:
        print("   ", row.tolist())
    print(f"  false negatives (malignant predicted benign): {false_negatives}")
    print(f"  false positives (benign predicted malignant): {false_positives}")

    rule("7. The verdict, with an interval")
    se, half_width, lower, upper = c.verdict_interval(test_acc, len(y_test))
    print(f"  n_test = {len(y_test)}  se = {se:.4f}  95 percent half-width = +/-{half_width:.4f}")
    print(f"  95 percent interval: [{lower:.4f}, {upper:.4f}]")
    improvement = round(test_acc - baseline_acc, 4)
    print(f"  improvement over baseline: {improvement:+.4f}")
    print(f"  distinguishable from baseline at this test-set size: {c.distinguishable_from_baseline(test_acc, baseline_acc, len(y_test))}")

    rule("8. The leaky version: selecting by peeking at the test set")
    leaky = c.leaky_selection_test_score(x_train, y_train, x_test, y_test)
    print(f"  honest (select on CV, look once): {test_acc:.4f}")
    print(f"  leaky (best of {k} scored directly on test): {leaky:.4f}")
    print(f"  gap: {round(leaky - test_acc, 4):+.4f}")

    rule("8b. The leaky gap, over 20 seeds")
    rows2 = c.leaky_vs_honest_over_seeds(X, y, seeds=range(20))
    gaps = np.array([r[3] for r in rows2])
    print("   seed   honest    leaky      gap")
    for seed, honest_s, leaky_s, gap_s in rows2:
        print(f"  {seed:5d}   {honest_s:.4f}   {leaky_s:.4f}   {gap_s:+.4f}")
    print(f"  mean gap: {float(gaps.mean()):+.4f}  sd {float(gaps.std()):.4f}  min {float(gaps.min()):+.4f}  max {float(gaps.max()):+.4f}")
    print(f"  fraction of seeds where the leak was non-negative: {float((gaps >= 0).mean()):.4f}")

    rule("9. What the whole thing costs")
    print("  wall-clock cost is machine-dependent and not reproduced here byte for byte;")
    print("  see metadata.yml and expected-output/FIELDS.md for the captured timing")


if __name__ == "__main__":
    main()
