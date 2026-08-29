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

import regression_lib as r  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 150 -- multiple and polynomial regression, measured")
    print("=" * 55)

    X, y, names = r.load_raw_diabetes()

    rule("1. Correlation and variance inflation, ten raw-unit predictors")
    vifs = r.variance_inflation_factors(X, names)
    print("  name    VIF")
    for name in names:
        print(f"  {name:<5}   {vifs[name]:>8.4f}")
    print(f"  correlation(s1, s2) : {r.correlation(X, names, 's1', 's2'):+.4f}")
    print(f"  correlation(s3, s4) : {r.correlation(X, names, 's3', 's4'):+.4f}")
    print(f"  correlation(bmi, bp): {r.correlation(X, names, 'bmi', 'bp'):+.4f}")

    rule("2. The centrepiece: an exact duplicate of s1")
    idx_s1 = names.index("s1")
    original, coef_a, coef_b, max_diff, r2_orig, r2_dup = r.duplicate_column_exact(X, y, idx_s1)
    print(f"  original s1 coefficient        : {original:+.4f}")
    print(f"  duplicate model, coefficient a : {coef_a:+.4f}")
    print(f"  duplicate model, coefficient b : {coef_b:+.4f}")
    print(f"  sum of the two                 : {coef_a + coef_b:+.4f}")
    print(f"  max abs prediction difference  : {max_diff:.2e}")
    print(f"  R2 original / duplicate        : {r2_orig:.4f} / {r2_dup:.4f}")

    rule("3. Breaking the tie with noise")
    noise_scale = 0.01 * float(X[:, idx_s1].std())
    coef_a, coef_b, coef_sum, max_diff, r2 = r.duplicate_column_noisy(X, y, idx_s1, noise_scale, seed=0)
    print(f"  noise scale (1% of s1's std)   : {noise_scale:.4f}")
    print(f"  seed 0, coefficient a          : {coef_a:+.4f}")
    print(f"  seed 0, coefficient b          : {coef_b:+.4f}")
    print(f"  seed 0, sum                    : {coef_sum:+.4f}")
    print(f"  seed 0, R2                     : {r2:.4f}")
    spread10 = r.duplicate_noisy_spread(X, y, idx_s1, noise_scale, range(10))
    print(f"  across seeds 0-9, coefficient a : {spread10['coef_a']}")
    print(f"  across seeds 0-9, coefficient b : {spread10['coef_b']}")
    print(f"  across seeds 0-9, sum           : {spread10['sum']}")
    print(f"  largest single prediction move : {spread10['max_pred_diff_overall']:.4f}")
    print(f"  across seeds 0-9, R2            : {spread10['r2']}")

    rule("4. Bootstrap coefficient instability, all ten predictors")
    boot = r.bootstrap_coefficient_spread(X, y, names, reps=500, seed=0)
    print("  name    mean       sd        cv")
    for name in names:
        row = boot[name]
        cv = "  n/a " if row["cv"] is None else f"{row['cv']:.4f}"
        print(f"  {name:<5}   {row['mean']:>8.4f}   {row['sd']:>7.4f}   {cv}")

    rule("5. Holding the other nine predictors constant flips a sign")
    svm = r.simple_vs_multiple_coefficients(X, y, names)
    print("  name    simple      multiple    sign flip")
    for name in names:
        row = svm[name]
        print(f"  {name:<5}   {row['simple']:>9.4f}   {row['multiple']:>9.4f}   {row['sign_flip']}")

    rule("6. A polynomial fit is linear in its parameters")
    idx_bmi, idx_bp = names.index("bmi"), names.index("bp")
    X2 = X[:, [idx_bmi, idx_bp]]
    poly_names, sk_coefs, sk_intercept, ne_coefs, ne_intercept, coef_diff, intercept_diff = (
        r.polynomial_matches_normal_equations(X2, y, degree=2, feature_names=["bmi", "bp"])
    )
    print(f"  design matrix columns   : {poly_names}")
    print(f"  sklearn coefficients    : {sk_coefs}")
    print(f"  normal-eq coefficients  : {ne_coefs}")
    print(f"  sklearn intercept       : {sk_intercept}")
    print(f"  normal-eq intercept     : {ne_intercept}")
    print(f"  max abs coefficient gap : {coef_diff:.2e}")
    print(f"  max abs intercept gap   : {intercept_diff:.2e}")
    r2_with, r2_without, interaction_coef = r.interaction_term_effect(X2, y)
    print(f"  R2 with 'bmi bp' term   : {r2_with:.6f}")
    print(f"  R2 without it           : {r2_without:.6f}")
    print(f"  interaction coefficient : {interaction_coef:.6f}")

    rule("7. R2 never decreases when you add a predictor -- even noise")
    rows = r.r2_with_added_noise_columns(X, y, [1, 2, 5, 10], seed=42)
    print("  noise columns   R2         delta vs 10 real predictors")
    for n_noise, r2, delta in rows:
        print(f"  {n_noise:>13d}   {r2:.6f}   {delta:+.6f}")

    rule("8. Standardising changes the coefficients, not the model")
    raw_coefs, scaled_coefs, r2_raw, r2_scaled, max_pred_diff = r.scaling_effect(X, y)
    print("  name    raw coef     scaled coef")
    for name, raw_c, scaled_c in zip(names, raw_coefs, scaled_coefs):
        print(f"  {name:<5}   {raw_c:>9.4f}   {scaled_c:>10.4f}")
    print(f"  R2 raw / scaled                : {r2_raw:.6f} / {r2_scaled:.6f}")
    print(f"  max abs prediction difference  : {max_pred_diff:.2e}")


if __name__ == "__main__":
    main()
