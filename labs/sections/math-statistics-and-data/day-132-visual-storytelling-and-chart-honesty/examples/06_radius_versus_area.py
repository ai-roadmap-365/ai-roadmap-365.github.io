"""Exercise 6 — encoding by radius squares every ratio.

Day 127 named this; here it is as a number. Two bubbles, values 25 and
100, a data ratio of 4. Encode by area and the drawn areas are in the
ratio 4. Encode by radius -- which is what "make the circle four times as
big" means to most people -- and the drawn areas are in the ratio 16.
"""

import matplotlib.pyplot as plt

import honesty as H

VALUES = (25.0, 100.0)


def main():
    data_ratio = VALUES[1] / VALUES[0]
    print(f"Two bubbles for {VALUES[0]:.0f} and {VALUES[1]:.0f}. Data ratio = {data_ratio:.1f}.")
    print()

    measured = {}
    for encoding in ("area", "radius"):
        fig, ax = H.bubble_pair(VALUES, encode=encoding)
        try:
            fig.canvas.draw()
            area_ratio = H.drawn_area_ratio(ax)
        finally:
            plt.close(fig)
        factor = H.lie_factor(area_ratio, data_ratio)
        measured[encoding] = (area_ratio, factor)
        print(f"  encode by {encoding:<7} drawn area ratio {area_ratio:>6.2f}   lie factor {factor:>5.2f}")
    print()

    area_ratio_correct, factor_correct = measured["area"]
    area_ratio_wrong, factor_wrong = measured["radius"]

    assert abs(factor_correct - 1.0) < 1e-9, factor_correct
    assert abs(area_ratio_wrong - data_ratio**2) < 1e-9, area_ratio_wrong
    assert abs(factor_wrong - data_ratio) < 1e-9, factor_wrong

    print("  Stated precisely, because the sloppy version of this is easy to")
    print("  get backwards:")
    print(f"    the SHOWN AREA RATIO is the square of the data ratio")
    print(f"      {area_ratio_wrong:.1f} = {data_ratio:.1f} squared")
    print(f"    so the LIE FACTOR equals the data ratio itself")
    print(f"      {factor_wrong:.1f} = {area_ratio_wrong:.1f} / {data_ratio:.1f}")
    print()
    print("  Which means the distortion gets worse the bigger the real")
    print("  difference is -- the chart exaggerates most exactly where the")
    print("  reader is paying most attention.")
    print()
    print("  matplotlib's scatter takes `s` as area in points squared, so the")
    print("  correct encoding, s proportional to the value, is the one that")
    print("  looks like it is doing less work.")
    print()
    print("06_radius_versus_area.py: every assertion held.")


if __name__ == "__main__":
    main()
