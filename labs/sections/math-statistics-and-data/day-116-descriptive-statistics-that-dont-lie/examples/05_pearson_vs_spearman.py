"""Exercise 5: Pearson measures LINEAR association only; Spearman measures
MONOTONE association. A perfect parabola fools Pearson; a perfect (but
non-linear) monotone curve does not fool Spearman."""

import dataset as D
import descriptive as F


def main() -> None:
    print(f"parabola x = {D.PARABOLA_X}")
    print(f"parabola y = x^2 = {D.PARABOLA_Y}")
    pear_parabola = F.pearson(D.PARABOLA_X, D.PARABOLA_Y)
    print(f"  Pearson correlation  = {pear_parabola}")
    assert abs(pear_parabola) < D.PARABOLA_PEARSON_TOLERANCE
    print("  -> essentially zero, despite y being EXACTLY determined by x")

    print()
    print(f"monotone x = {D.MONOTONE_X}")
    print(f"monotone y = x^3 = {D.MONOTONE_Y}")
    pear_monotone = F.pearson(D.MONOTONE_X, D.MONOTONE_Y)
    spear_monotone = F.spearman(D.MONOTONE_X, D.MONOTONE_Y)
    print(f"  Pearson correlation  = {pear_monotone:.6f}  (strong, but not perfect)")
    print(f"  Spearman correlation = {spear_monotone:.6f}  (exactly 1.0)")
    assert spear_monotone == 1.0
    assert pear_monotone < 1.0  # the cubic is not a straight line

    print()
    print(
        "Same shape of evidence, two different questions: Pearson asks "
        "'how well does a straight line fit', Spearman asks 'does y always "
        "increase when x does'. The parabola answers the first question "
        "with 'not at all' and would answer the second with 'no' too, "
        "since it isn't monotone. The cubic answers the first with "
        "'pretty well' and the second with 'perfectly'."
    )
    print("05_pearson_vs_spearman.py: every assertion held.")


if __name__ == "__main__":
    main()
