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
from sklearn.linear_model import LinearRegression  # noqa: E402

import regression_lib as r  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 153 -- linear regression from scratch, measured")
    print("=" * 52)

    X, y = r.load_diabetes_data(scaled=True)
    n, p = X.shape

    rule("1. Three closed forms on well-conditioned data")
    A = r.add_intercept_column(X)
    beta_ne = r.fit_normal_equations(A, y)
    beta_lstsq = r.fit_lstsq(A, y)
    beta_sk = r.sklearn_reference_fit(X, y)
    gap_ne = r.max_abs_difference(beta_ne, beta_sk)
    gap_lstsq = r.max_abs_difference(beta_lstsq, beta_sk)
    print(f"  max |normal equations - sklearn| : {gap_ne:.4e}")
    print(f"  max |lstsq            - sklearn| : {gap_lstsq:.4e}")
    print(f"  lstsq is {gap_ne / gap_lstsq:.1f}x closer to sklearn's own answer")

    rule("1b. The normal equations square the condition number")
    cond_a, cond_ata = r.condition_numbers(A)
    print(f"  condition number of X (with intercept) : {cond_a:.4f}")
    print(f"  condition number of X'X                : {cond_ata:.4f}")
    print(f"  cond(X'X) / cond(X)^2                   : {cond_ata / cond_a**2:.10f}")

    rule("2. A near-duplicate column, and three very different answers")
    Xd, yd, true_coef = r.make_dramatic_collinear_dataset(n=100, seed=0)
    Ad = r.add_intercept_column(Xd)
    beta_ne_d = r.fit_normal_equations(Ad, yd)
    beta_lstsq_d = r.fit_lstsq(Ad, yd)
    beta_sk_d = r.sklearn_reference_fit(Xd, yd)
    print("  true coefficients (intercept, c0, c1, c2, c3-duplicate)")
    print(f"    = [0.0, {true_coef[0]:.1f}, {true_coef[1]:.1f}, {true_coef[2]:.1f}, {true_coef[3]:.1f}]")
    print(f"  normal-equation coefficients : {np.round(beta_ne_d, 3).tolist()}")
    print(f"  lstsq coefficients           : {np.round(beta_lstsq_d, 3).tolist()}")
    print(f"  sklearn coefficients         : {np.round(beta_sk_d, 3).tolist()}")

    rule("2b. And the squaring relationship itself becomes hard to verify")
    cond_ad, cond_atad = r.condition_numbers(Ad)
    print(f"  condition number of X (with intercept) : {cond_ad:.4e}")
    print(f"  condition number of X'X                : {cond_atad:.4e}")
    print(f"  cond(X'X) / cond(X)^2                   : {cond_atad / cond_ad**2:.4f}")

    rule("3. Gradient descent versus the closed form, standardized features")
    Xs = r.standardize(X)
    yc = y - y.mean()
    target = r.fit_normal_equations(Xs, yc)
    threshold = r.stability_threshold(Xs)
    eig_s = r.hessian_eigenvalues(Xs, n)
    print(f"  stability threshold (Day 111, |1 - eta*a| < 1) : {threshold:.4f}")
    print(f"  Hessian eigenvalue ratio (max/min)             : {eig_s.max() / eig_s.min():.4f}")
    lr = 0.2
    iters_3, _ = r.iters_to_tolerance(Xs, yc, lr, target, 5e-4, 200_000)
    iters_6, _ = r.iters_to_tolerance(Xs, yc, lr, target, 5e-7, 200_000)
    iters_9, _ = r.iters_to_tolerance(Xs, yc, lr, target, 5e-10, 200_000)
    print(f"  at lr={lr} (80 percent of threshold):")
    print(f"    iterations to agree to 3 decimals : {iters_3}")
    print(f"    iterations to agree to 6 decimals : {iters_6}")
    print(f"    iterations to agree to 9 decimals : {iters_9}")

    rule("3b. The same setup on raw, unscaled features")
    Xraw, yraw = r.load_diabetes_data(scaled=False)
    Xrc, yrc, _, _ = r.center(Xraw, yraw)
    eig_r = r.hessian_eigenvalues(Xrc, n)
    raw_threshold = r.stability_threshold(Xrc)
    target_r = r.fit_normal_equations(Xrc, yrc)
    print(f"  stability threshold, raw features : {raw_threshold:.6e}")
    print(f"  Hessian eigenvalue ratio, raw      : {eig_r.max() / eig_r.min():.4f}")
    status, coef_r = r.iters_to_tolerance(Xrc, yrc, raw_threshold * 0.95, target_r, 5e-4, 200_000)
    print(f"  at 95 percent of ITS OWN threshold, after 200000 iterations:")
    print(f"    converged to 3 decimals? {status is not None}")
    print(f"    remaining max |coef - closed form| : {r.max_abs_difference(coef_r, target_r):.4f}")

    rule("4. The stability threshold predicts divergence exactly")
    below_status, _ = r.iters_to_tolerance(Xs, yc, threshold * 0.8, target, 1e-9, 20_000)
    above_status, above_coef = r.iters_to_tolerance(Xs, yc, threshold * 1.02, target, 1e-9, 20_000)
    print(f"  at 80 percent of threshold  (lr={threshold * 0.8:.4f}): converges in {below_status} iterations")
    print(f"  at 102 percent of threshold (lr={threshold * 1.02:.4f}): {above_status}, finite={np.all(np.isfinite(above_coef))}")

    rule("5. Operations, not time")
    ops_normal = r.normal_equation_op_count(n, p + 1)
    ops_gd = r.gradient_descent_op_count(n, p, iters_9)
    print(f"  normal-equation operations (form X'X, O(n p^2), plus solve, O(p^3)) : {ops_normal:,}")
    print(f"  gradient-descent operations ({iters_9} iterations, O(n p) each)      : {ops_gd:,}")
    print(f"  ratio                                                              : {ops_gd / ops_normal:.2f}x")

    rule("6. A scikit-learn-compatible estimator, checked by the library itself")
    sk = LinearRegression().fit(Xs, y)
    normal_est = r.OLSRegressor(method="normal").fit(Xs, y)
    lstsq_est = r.OLSRegressor(method="lstsq").fit(Xs, y)
    gd_est = r.OLSRegressor(method="gd", lr=0.2, n_iter=8000).fit(Xs, y)
    print(f"  max |normal-method coef  - sklearn| : {r.max_abs_difference(normal_est.coef_, sk.coef_):.4e}")
    print(f"  max |lstsq-method coef   - sklearn| : {r.max_abs_difference(lstsq_est.coef_, sk.coef_):.4e}")
    print(f"  max |gd-method coef      - sklearn| : {r.max_abs_difference(gd_est.coef_, sk.coef_):.4e}")
    passed, failed, skipped = r.run_check_estimator(r.OLSRegressor())
    print(f"  check_estimator: {len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped, {len(passed) + len(failed) + len(skipped)} total")
    for name, _msg in failed:
        print(f"    FAILED : {name}")
    for name, _msg in skipped:
        print(f"    SKIPPED: {name}")

    rule("7. fit_intercept: centring versus an appended column of ones")
    coef_col, intercept_col, coef_centred, intercept_centred = r.fit_intercept_two_ways(X, y)
    print(f"  max |coef_column - coef_centred| : {r.max_abs_difference(coef_col, coef_centred):.4e}")
    print(f"  |intercept_column - intercept_centred| : {abs(intercept_col - intercept_centred):.4e}")


if __name__ == "__main__":
    main()
