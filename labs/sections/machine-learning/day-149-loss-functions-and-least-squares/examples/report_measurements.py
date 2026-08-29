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

import loss_lib as L  # noqa: E402

VALUES = [2.0, 3.0, 5.0, 7.0, 100.0]


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 149 -- loss functions and least squares, measured")
    print("=" * 55)

    rule("1. What each loss minimises")
    best_sq = L.grid_minimize(VALUES, L.sse, 0.0, 110.0)
    best_abs = L.grid_minimize(VALUES, L.sae, 0.0, 110.0)
    print(f"  values: {VALUES}")
    print(f"  mean   = {np.mean(VALUES):.4f}   grid argmin of squared error = {best_sq:.5f}")
    print(f"  median = {np.median(VALUES):.4f}    grid argmin of absolute error = {best_abs:.5f}")

    rule("2. The shape of the loss landscape")
    x, y = L.make_line_data(n=40, seed=3)
    slopes = np.round(np.arange(2.0, 4.01, 0.1), 4)
    sq_losses, abs_losses = L.loss_landscape(x, y, intercept=5.0, slopes=slopes)
    print(f"  argmin, squared-error slope  : {slopes[int(np.argmin(sq_losses))]}")
    print(f"  argmin, absolute-error slope : {slopes[int(np.argmin(abs_losses))]}")
    print(f"  sd of squared-error's second differences  : {np.std(L.second_differences(sq_losses)):.6f} (constant -> parabola)")
    print(f"  sd of absolute-error's second differences : {np.std(L.second_differences(abs_losses)):.4f} (varies -> kinked)")

    rule("3. The normal equations, squared error's closed form")
    x3, y3 = L.make_line_data(n=300, seed=2)
    intercept_eq, slope_eq = L.normal_equations(x3, y3)
    intercept_sk, slope_sk = L.fit_ols(x3, y3)
    print(f"  normal equations : intercept={intercept_eq:.6f}  slope={slope_eq:.6f}")
    print(f"  LinearRegression : intercept={intercept_sk:.6f}  slope={slope_sk:.6f}")
    print(f"  difference       : intercept={abs(intercept_eq - intercept_sk):.2e}  slope={abs(slope_eq - slope_sk):.2e}")

    rule("4. Outlier sensitivity: one point, moved 80 units off the line")
    x4, y4 = L.make_line_data(n=60, seed=1, noise_sd=1.5)
    result = L.outlier_shift(x4, y4, outlier_offset=80.0)
    print("  estimator    before     after    movement")
    for name in ("ols", "huber", "quantile"):
        r = result[name]
        print(f"  {name:9s}  {r['before']:.4f}    {r['after']:.4f}    {r['movement']:+.4f}")
    ols_move = abs(result["ols"]["movement"])
    print(f"  OLS moved {ols_move / abs(result['huber']['movement']):.1f}x further than Huber, "
          f"{ols_move / abs(result['quantile']['movement']):.1f}x further than the median fit")

    rule("5. Huber's delta, sweeping from absolute-error-like to squared-error-like")
    y_outlier = np.asarray(y4, dtype=float).copy()
    y_outlier[int(np.argmax(x4))] += 80.0
    sweep = L.huber_epsilon_sweep(x4, y_outlier, [1.0, 1.35, 1.5, 2.0, 5.0, 20.0, 100.0])
    print("  epsilon      slope")
    for eps, slope in sweep:
        print(f"  {eps:7.2f}   {slope:.4f}")
    ols_intercept, ols_slope = L.fit_ols(x4, y_outlier)
    print(f"  OLS on the same outlier-contaminated data: slope={ols_slope:.4f} -- matches the large-epsilon end of the sweep")

    rule("6. What squared error assumes about the errors")
    gauss = L.efficiency_under_noise(heavy_tailed=False, replications=500)
    heavy = L.efficiency_under_noise(heavy_tailed=True, replications=500)
    print("  500 replications, n=150 rows each, true slope 3.0")
    print(f"  Gaussian errors     : OLS mean={gauss[0]:.4f} sd={gauss[1]:.4f}   Huber mean={gauss[2]:.4f} sd={gauss[3]:.4f}")
    print(f"    ratio sd(OLS)/sd(Huber) = {gauss[1] / gauss[3]:.4f}  (below 1: OLS is the more efficient choice)")
    print(f"  heavy-tailed errors : OLS mean={heavy[0]:.4f} sd={heavy[1]:.4f}   Huber mean={heavy[2]:.4f} sd={heavy[3]:.4f}")
    print(f"    ratio sd(OLS)/sd(Huber) = {heavy[1] / heavy[3]:.4f}  (above 1: Huber is now the more efficient choice)")
    print("  both estimators stay close to unbiased in both settings; only the spread changes")


if __name__ == "__main__":
    main()
