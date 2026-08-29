#!/usr/bin/env python3
"""Print every measured pair in this lab as one table.

The harness compares this output byte for byte against
expected-output/measured-values.txt, so the report is not a convenience:
it is how the lab notices that a number in the lesson has gone stale.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import regression_metrics_lib as m  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 152 -- regression metrics, measured")
    print("=" * 41)

    rule("1. Train R2 climbs on pure-noise columns")
    print("  n_noise   n_rows   n_predictors   train_r2   adjusted_r2")
    for n_noise, n_rows, n_predictors, r2, adj in m.noise_column_r2_curve():
        print(f"  {n_noise:7d}   {n_rows:6d}   {n_predictors:12d}   {r2:.4f}     {adj:.4f}")
    print("  every added column is independent noise, unrelated to the target")

    rule("2. R2 is not bounded below by zero")
    print(f"  full 10-feature model, test R2       : {m.full_model_test_r2():.4f}")
    print(f"  constant-mean predictor, test R2     : {m.constant_mean_test_r2():.4f}")
    print(f"  deliberately bad (all-zeros), test R2: {m.bad_predictor_test_r2():.4f}")

    rule("3. RMSE versus MAE under one outlier")
    rmse_before, mae_before, rmse_after, mae_after = m.rmse_mae_outlier_shift()
    print(f"  before: RMSE {rmse_before:.4f}  MAE {mae_before:.4f}")
    print(f"  after : RMSE {rmse_after:.4f}  MAE {mae_after:.4f}  (one target moved +200)")
    print(f"  RMSE moved by a factor of {rmse_after / rmse_before:.2f}")
    print(f"  MAE moved by a factor of {mae_after / mae_before:.2f}")

    rule("4. MAPE breaking")
    print(f"  MAPE with one true value exactly zero      : {m.mape_at_zero_target():.4e}")
    mape_nz, mae_nz = m.mape_near_zero_target()
    print(f"  MAPE with a true value of 0.5 in the mix   : {mape_nz:.4f}  (MAE on the same rows: {mae_nz:.4f})")
    max_under, ten_x_over = m.mape_asymmetry_bound()
    print(f"  MAPE of the worst possible under-prediction: {max_under:.4f}")
    print(f"  MAPE of an eleven-times over-prediction    : {ten_x_over:.4f}")
    print("  under-prediction is capped at 1.0; over-prediction is not")

    rule("5. A metric ranking inversion")
    rmse_a, mae_a, rmse_b, mae_b = m.ranking_inversion_models()
    print(f"  Model A (many small errors)      : RMSE {rmse_a:.4f}  MAE {mae_a:.4f}")
    print(f"  Model B (few large errors)       : RMSE {rmse_b:.4f}  MAE {mae_b:.4f}")
    print(f"  RMSE prefers: {'A' if rmse_a < rmse_b else 'B'}")
    print(f"  MAE prefers : {'A' if mae_a < mae_b else 'B'}")

    rule("6. RMSE and MAE carry the target's units")
    results = m.raw_and_scaled_metrics()
    for label, (r, a, r2) in results.items():
        print(f"  {label:7s} features: RMSE {r:.4f}  MAE {a:.4f}  R2 {r2:.4f}")
    print("  identical either way -- ordinary least squares is invariant to")
    print("  a per-column affine rescaling of its inputs")

    rule("7. r2_score: agreement, and the argument-order bug")
    from_metric, from_model = m.r2_score_vs_model_score()
    print(f"  r2_score(y_test, pred)         : {from_metric:.6f}")
    print(f"  model.score(X_test, y_test)    : {from_model:.6f}")
    correct_order, swapped_order = m.r2_score_argument_order()
    print(f"  r2_score(y_test, pred)  correct : {correct_order:.6f}")
    print(f"  r2_score(pred, y_test) swapped : {swapped_order:.6f}")


if __name__ == "__main__":
    main()
