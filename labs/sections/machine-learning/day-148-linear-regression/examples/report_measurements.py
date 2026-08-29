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
    print("Day 148 -- linear regression, measured")
    print("=" * 39)

    rule("1. The line itself: BMI against disease progression, raw units")
    bmi, y = r.load_bmi_and_target()
    model = r.fit_line(bmi, y)
    residuals = y - model.predict(bmi)
    se = r.slope_standard_error(bmi, residuals)
    ci = r.confidence_interval(float(model.coef_[0]), se)
    predicted_at_mean, mean_y, diff = r.passes_through_the_means(model, bmi, y)
    print(f"  n = {len(y)}, BMI range {bmi.min():.1f}-{bmi.max():.1f}, target range {y.min():.1f}-{y.max():.1f}")
    print(f"  slope     : {model.coef_[0]:.4f}  (points of progression per unit of BMI)")
    print(f"  intercept : {model.intercept_:.4f}")
    print(f"  R-squared : {model.score(bmi, y):.4f}")
    print(f"  slope SE  : {se:.4f}   95% CI [{ci[0]}, {ci[1]}]   t = {model.coef_[0] / se:.2f}")
    print(f"  predicted at mean BMI : {predicted_at_mean:.4f}   mean of y : {mean_y:.4f}   diff : {diff:.2e}")
    print(f"  sum of residuals      : {r.residual_sum(residuals):.2e}")

    rule("2. Recovering a slope you know to be true (true slope = 5.0)")
    print("       n   mean abs error")
    for n, err in r.slope_recovery_error([20, 50, 200, 1000, 5000]):
        print(f"  {n:6d}   {err:.4f}")
    by_n = dict(r.slope_recovery_error([20, 50, 200, 1000, 5000]))
    print(f"  ratio, n=20 to n=200  : {by_n[200] / by_n[20]:.4f}   (predicted ~ 1/sqrt(10) = {1 / np.sqrt(10):.4f})")
    print(f"  ratio, n=20 to n=5000 : {by_n[5000] / by_n[20]:.4f}   (predicted ~ 1/sqrt(250) = {1 / np.sqrt(250):.4f})")

    rule("3. Curvature: a fit that looks fine and is not")
    xc, yc = r.curved_dataset()
    model_c = r.fit_line(xc, yc)
    residuals_c = yc - model_c.predict(xc)
    print(f"  R-squared of the line : {model_c.score(xc, yc):.4f}   (looks respectable)")
    print("  mean residual by bin of x (positive, negative, positive: the missed curve)")
    for mean_x, mean_resid in r.binned_residual_means(xc, residuals_c, bins=5):
        print(f"    x ~ {mean_x:5.2f}   mean residual {mean_resid:+.4f}")
    quad_r2 = r.quadratic_fit_r_squared(xc, residuals_c)
    corr = float(np.corrcoef(residuals_c, xc.flatten() ** 2)[0, 1])
    print(f"  quadratic fit to the residuals, R-squared : {quad_r2:.4f}")
    print(f"  correlation of residuals with x^2         : {corr:.4f}")

    rule("4. Heteroscedasticity: error that grows with x")
    xh, yh = r.heteroscedastic_dataset()
    model_h = r.fit_line(xh, yh)
    residuals_h = yh - model_h.predict(xh)
    low_sd, high_sd = r.residual_spread_by_half(xh, residuals_h)
    print(f"  R-squared of the line : {model_h.score(xh, yh):.4f}   (also looks fine)")
    print(f"  residual sd, low half of x  : {low_sd:.4f}")
    print(f"  residual sd, high half of x : {high_sd:.4f}")
    print(f"  ratio                       : {high_sd / low_sd:.4f}")

    rule("5. One point that moves the line")
    xl, yl = r.leverage_dataset()
    model_without = r.fit_line(xl.reshape(-1, 1), yl)
    xl_with, yl_with = r.add_point(xl, yl, x_new=40.0, y_new=5.0)
    model_with = r.fit_line(xl_with.reshape(-1, 1), yl_with)
    leverage_new = r.leverage_of_point(xl_with, 40.0)
    typical = r.mean_leverage_excluding(xl_with, 40.0)
    print(f"  slope, 40 ordinary points        : {model_without.coef_[0]:.4f}")
    print(f"  slope, plus one leverage point    : {model_with.coef_[0]:.4f}")
    print(f"  change                            : {model_with.coef_[0] - model_without.coef_[0]:+.4f}")
    print(f"  leverage of the added point        : {leverage_new:.4f}")
    print(f"  mean leverage of the other 40      : {typical:.4f}")
    print(f"  ratio                              : {leverage_new / typical:.2f}")

    rule("6. fit_intercept=False, and what it costs")
    xi, yi = r.intercept_dataset()
    model_yes = r.fit_line(xi, yi, fit_intercept=True)
    model_no = r.fit_line(xi, yi, fit_intercept=False)
    rmse_yes = r.rmse(yi, model_yes.predict(xi))
    rmse_no = r.rmse(yi, model_no.predict(xi))
    print(f"  true intercept = 25.0, true slope = 3.0, x never near zero")
    print(f"  fit_intercept=True  : slope {model_yes.coef_[0]:.4f}  intercept {model_yes.intercept_:.4f}  RMSE {rmse_yes:.4f}")
    print(f"  fit_intercept=False : slope {model_no.coef_[0]:.4f}  intercept {model_no.intercept_:.4f}  RMSE {rmse_no:.4f}")
    print(f"  RMSE ratio (false/true) : {rmse_no / rmse_yes:.4f}")

    rule("7. Telling curvature apart from noise")
    quad_r2_bmi = r.quadratic_fit_r_squared(bmi, residuals)
    skew = r.skewness(residuals)
    print(f"  quadratic fit to the BMI model's own residuals, R-squared : {quad_r2_bmi:.4f}")
    print(f"  (contrast with section 3's 0.3558 on data with real curvature)")
    print(f"  skewness of the BMI model's residuals : {skew:.4f}")


if __name__ == "__main__":
    main()
