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
from sklearn.dummy import DummyRegressor  # noqa: E402

import regression_lib as r  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 154 -- a complete regression project, measured")
    print("=" * 51)

    rule("1. The dataset: the only bundled regression set")
    X, y, names = r.load_dataset()
    print(f"  shape: {X.shape}  features: {names}")
    print(f"  y range: [{float(y.min()):.1f}, {float(y.max()):.1f}]  mean: {float(y.mean()):.4f}")
    print("  the target is a composite disease-progression score with no physical unit")

    x_train, x_test, y_train, y_test = r.split_once(X, y, seed=0)
    print(f"  split: train={x_train.shape[0]}  test={x_test.shape[0]}  (seed 0, 25 percent test)")

    rule("2. The baseline, before any model")
    base_rmse, base_r2 = r.baseline_metrics(x_train, y_train, x_test, y_test)
    print(f"  mean-predictor baseline: RMSE {base_rmse:.4f}  R2 {base_r2:.4f}")

    rule("3. The sweep: cross-validate every candidate on train rows only")
    k = r.candidate_count()
    print(f"  K = {k} candidate pipelines: 11 ridge, 11 lasso, 1 plain OLS")
    family, param, cv_rmse, fitted = r.select_best(x_train, y_train, seed=0)
    print(f"  winner: {family} (alpha={param})  5-fold CV RMSE = {cv_rmse:.4f}")

    rule("4. ONE test evaluation")
    gate = r.GatedTestSet(x_test, y_test)
    test_rmse, test_r2, test_mae = gate.evaluate(fitted)
    print(f"  test RMSE: {test_rmse:.4f}  R2: {test_r2:.4f}  MAE: {test_mae:.4f}")
    try:
        gate.evaluate(fitted)
        print("  second evaluation: NO ERROR RAISED")
    except r.TestSetTouchedTwice as exc:
        print(f"  second evaluation : {type(exc).__name__}")
        print(f"    {exc}")

    rule("5. The margin, with a bootstrap interval")
    baseline_model = DummyRegressor(strategy="mean").fit(x_train, y_train)
    pred_baseline = baseline_model.predict(x_test)
    pred_model = fitted.predict(x_test)
    margin = round(base_rmse - test_rmse, 4)
    lower, upper = r.margin_bootstrap_interval(y_test, pred_baseline, pred_model, seed=0)
    print(f"  margin (baseline RMSE - model RMSE): {margin:+.4f}")
    print(f"  95 percent bootstrap interval on the margin: [{lower:.4f}, {upper:.4f}]")
    print(f"  distinguishable from baseline at this test-set size: {r.margin_distinguishable(lower, upper)}")

    rule("6. Residual diagnostics -- the centrepiece")
    resid_mean, resid_std = r.residual_summary(y_test, pred_model)
    het = r.heteroscedasticity_signal(pred_model, y_test)
    curv = r.curvature_signal(pred_model, y_test)
    qq = r.normal_probability_correlation(y_test, pred_model)
    print(f"  residuals: mean {resid_mean:+.4f}  sd {resid_std:.4f}")
    print(f"  heteroscedasticity signal, corr(fitted, |residual|): {het:+.4f}")
    print(f"  curvature signal, corr(fitted^2, residual): {curv:+.4f}")
    print(f"  normal-probability (Q-Q) correlation: {qq:.4f}")
    print("  largest residuals (row, true, predicted, residual):")
    for row_idx, true_val, pred_val, resid in r.largest_residuals(y_test, pred_model, n=5):
        print(f"    row {row_idx:3d}: true={true_val:7.1f}  pred={pred_val:7.1f}  residual={resid:+8.1f}")

    rule("7. Is the model worse for high-value targets?")
    rmse_low, rmse_high, ratio = r.error_by_target_level(y_test, pred_model)
    print(f"  RMSE on below-median targets: {rmse_low:.4f}")
    print(f"  RMSE on above-median targets: {rmse_high:.4f}")
    print(f"  ratio (high / low): {ratio:.4f}")

    rule("8. The leaky version: selecting by peeking at the test set")
    leaky_rmse = r.leaky_selection_test_rmse(x_train, y_train, x_test, y_test)
    print(f"  honest (select on CV, look once): {test_rmse:.4f}")
    print(f"  leaky (best of {k} scored directly on test): {leaky_rmse:.4f}")
    print(f"  gap (honest - leaky, positive means the leak looked better): {round(test_rmse - leaky_rmse, 4):+.4f}")

    rule("8b. The leaky gap, over 20 seeds")
    rows = r.leaky_vs_honest_over_seeds(X, y, seeds=range(20))
    gaps = np.array([row[3] for row in rows])
    print("   seed   honest    leaky      gap")
    for seed, honest_s, leaky_s, gap_s in rows:
        print(f"  {seed:5d}   {honest_s:.4f}   {leaky_s:.4f}   {gap_s:+.4f}")
    print(f"  mean gap: {float(gaps.mean()):+.4f}  sd {float(gaps.std()):.4f}  min {float(gaps.min()):+.4f}  max {float(gaps.max()):+.4f}")
    print(f"  fraction of seeds where the leak was non-negative: {float((gaps >= 0).mean()):.4f}")

    rule("9. Prediction intervals, and their realised coverage")
    half_width, coverage = r.prediction_interval_coverage(x_train, y_train, x_test, y_test, fitted, seed=0)
    print(f"  95 percent prediction interval half-width (from TRAIN out-of-fold residuals): +/-{half_width:.4f}")
    print(f"  realised coverage on the 111 test rows: {coverage:.4f}  (nominal: 0.9500)")

    rule("10. What the whole thing costs")
    print("  wall-clock cost is machine-dependent and not reproduced here byte for byte;")
    print("  see metadata.yml and expected-output/FIELDS.md for the captured timing")


if __name__ == "__main__":
    main()
