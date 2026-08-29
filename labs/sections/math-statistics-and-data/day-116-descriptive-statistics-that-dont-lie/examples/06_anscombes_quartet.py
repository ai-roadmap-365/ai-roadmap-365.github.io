"""Exercise 6: Anscombe's quartet. Four datasets that agree on every
familiar summary statistic to the documented precision -- and three shape
diagnostics that separate them completely, each for a different structural
reason.

Anscombe, F. J. (1973). "Graphs in Statistical Analysis."
The American Statistician, 27(1), 17-21.
"""

import dataset as D
import descriptive as F


def main() -> None:
    summaries = {name: F.anscombe_summary(x, y) for name, (x, y) in D.ANSCOMBE_SETS.items()}

    print(f"{'set':<5}{'mean x':>9}{'mean y':>9}{'var x':>9}{'var y':>9}{'r':>9}{'slope':>9}")
    for name, s in summaries.items():
        print(
            f"{name:<5}{s['mean_x']:>9.2f}{s['mean_y']:>9.2f}{s['var_x']:>9.2f}"
            f"{s['var_y']:>9.2f}{s['correlation']:>9.4f}{s['slope']:>9.4f}"
        )

    # All four sets agree to the documented precision on every classic
    # summary statistic.
    dec = D.ANSCOMBE_AGREEMENT_DECIMALS
    reference = summaries["I"]
    for name, s in summaries.items():
        assert round(s["mean_x"], dec) == round(reference["mean_x"], dec), name
        assert round(s["mean_y"], dec) == round(reference["mean_y"], dec), name
        assert round(s["var_x"], dec) == round(reference["var_x"], dec), name
        assert round(s["var_y"], dec) == round(reference["var_y"], dec), name
        assert round(s["correlation"], 1) == round(reference["correlation"], 1), name
        assert round(s["slope"], 1) == round(reference["slope"], 1), name

    print()
    print("Every classic summary statistic agrees. Three diagnostics those")
    print("summaries cannot see now tell the four sets apart:")
    print()

    shapes = {name: F.shape_statistics(x, y) for name, (x, y) in D.ANSCOMBE_SETS.items()}
    print(f"{'set':<5}{'max leverage':>14}{'outlier ratio':>15}{'sign changes':>14}")
    for name, s in shapes.items():
        print(
            f"{name:<5}{s['max_leverage']:>14.3f}{s['outlier_ratio']:>15.3f}"
            f"{s['residual_sign_changes']:>14.0f}"
        )

    # Set IV: the x-values are identical except for one, so ONE point
    # controls the entire slope -- its leverage swamps everyone else's,
    # while sets I, II and III (sharing the same x column) have identical,
    # unremarkable leverage.
    assert shapes["IV"]["max_leverage"] > 3.0 * shapes["I"]["max_leverage"]
    assert shapes["I"]["max_leverage"] == shapes["II"]["max_leverage"] == shapes["III"]["max_leverage"]

    # Set III: a perfect line plus one outlier -- that outlier's residual
    # dwarfs the combined residuals of every other point.
    assert shapes["III"]["outlier_ratio"] > 2.0 * shapes["I"]["outlier_ratio"]

    # Set II: a perfect parabola -- a straight line fit to it produces a
    # smooth, systematic curve of residuals that changes sign rarely,
    # unlike set I's honestly scattered noise, which flips sign often.
    assert shapes["II"]["residual_sign_changes"] < shapes["I"]["residual_sign_changes"]

    print()
    print(
        "Set IV's one non-repeated x-value carries most of the leverage. "
        "Set III's one outlier carries most of the residual. Set II's "
        "residuals trace a smooth curve instead of scattering. Set I is "
        "unremarkable on all three -- which is exactly what a genuinely "
        "linear relationship with honest noise should look like."
    )
    print("06_anscombes_quartet.py: every assertion held.")


if __name__ == "__main__":
    main()
