"""Exercise 3 — what a dual y-axis really does, and what it cannot do.

The folk version of this warning says two independently scaled axes let
you make any two series look correlated. Measured, that turns out to be
false in one specific way and true in two others, and the correction is
worth more than the folk version.

  * FALSE: the Pearson correlation of the two drawn traces cannot be
    changed by scaling at all. Across 500 random pairs of axis limits it
    stays equal to the data correlation to within 3e-15.
  * TRUE: its SIGN is a free parameter, exactly. Inverting one axis
    negates the drawn correlation with no change to the data.
  * TRUE, and the one that actually fools people: how close the two
    curves sit is entirely the author's choice, and a small gap is
    achievable whether the data correlate or not. So overlap is evidence
    of nothing.
"""

import matplotlib.pyplot as plt

import honesty as H


def measure(a, b, ylim_a, ylim_b, invert_b=False):
    if invert_b:
        ylim_b = (ylim_b[1], ylim_b[0])
    fig, ax, ax2 = H.dual_axis_figure(a, b, ylim_a=ylim_a, ylim_b=ylim_b)
    try:
        fig.canvas.draw()
        trace_a = H.drawn_trace(ax)
        trace_b = H.drawn_trace(ax2)
        return H.tracking_gap(trace_a, trace_b), H.pearson(trace_a, trace_b)
    finally:
        plt.close(fig)


def main():
    a, b = H.uncorrelated_pair()
    data_r = H.pearson(a, b)
    print(f"Two uncorrelated series, n={len(a)}. Data correlation r = {data_r:+.6f}")
    print("Series A runs around 50; series B runs around 0.004. Nothing below")
    print("touches the data. Only the four numbers passed to set_ylim change.")
    print()

    gap_apart, r_apart = measure(
        a, b, H.banded_limits(a, 0.55, 0.95), H.banded_limits(b, 0.05, 0.45)
    )
    gap_matched, r_matched = measure(a, b, H.matched_limits(a), H.matched_limits(b))
    gap_wide, r_wide = measure(a, b, H.widened_limits(a), H.widened_limits(b))
    _, r_inverted = measure(
        a, b, H.matched_limits(a), H.matched_limits(b), invert_b=True
    )

    print("  scaling                       drawn-trace gap   drawn-trace r")
    print(f"  parked in separate halves         {gap_apart:.4f}        {r_apart:+.6f}")
    print(f"  each filling the frame            {gap_matched:.4f}        {r_matched:+.6f}")
    print(f"  each axis widened 20x             {gap_wide:.4f}        {r_wide:+.6f}")
    print(f"  right axis inverted               (n/a)         {r_inverted:+.6f}")
    print()

    assert abs(r_apart - data_r) < 1e-12
    assert abs(r_matched - data_r) < 1e-12
    assert abs(r_wide - data_r) < 1e-12
    assert abs(r_inverted + data_r) < 1e-12, "inverting an axis must negate r exactly"
    assert gap_apart > 0.4, gap_apart
    assert gap_wide < 0.05, gap_wide

    print("  The visual impression moved from 'unrelated' (gap 0.49, two")
    print("  curves in different halves of the plot) to 'these track each")
    print(f"  other' (gap {gap_wide:.4f}, two curves lying on top of one another).")
    print("  The only correlation actually present never moved at all.")
    print()

    print("  Now the control that makes the last row mean something.")
    c, d = H.correlated_pair()
    strong_r = H.pearson(c, d)
    gap_strong, r_strong = measure(c, d, H.widened_limits(c), H.widened_limits(d))
    _, r_strong_inv = measure(
        c, d, H.matched_limits(c), H.matched_limits(d), invert_b=True
    )
    print(f"    a genuinely correlated pair, data r = {strong_r:+.6f}")
    print(f"    same 20x widening, gap = {gap_strong:.4f}")
    print(f"    uncorrelated pair,  gap = {gap_wide:.4f}")
    print(f"    right axis inverted, drawn r = {r_strong_inv:+.6f}")
    print()

    assert strong_r > 0.85, strong_r
    assert abs(r_strong - strong_r) < 1e-12
    assert abs(r_strong_inv + strong_r) < 1e-12
    assert gap_strong < 0.05 and gap_wide < 0.05, (gap_strong, gap_wide)

    print(f"  Both pairs draw as overlapping curves ({gap_strong:.4f} and {gap_wide:.4f}).")
    print(f"  One has r = {strong_r:+.3f}, the other r = {data_r:+.3f}. A reader who")
    print("  concludes 'these move together' from the picture has learned")
    print("  nothing about the data, because the picture is the same either way.")
    print()

    print("  And the invariance, measured rather than argued:")
    worst = 0.0
    import numpy as np

    rng = np.random.default_rng(1132)
    for _ in range(500):
        factor_a = float(rng.uniform(0.5, 50.0))
        factor_b = float(rng.uniform(0.5, 50.0))
        _, r_random = measure(
            a, b, H.widened_limits(a, factor_a), H.widened_limits(b, factor_b)
        )
        worst = max(worst, abs(r_random - data_r))
    print(f"    500 random pairs of axis limits, worst |drawn r - data r| = {worst:.2e}")
    assert worst < 1e-12, worst
    print()
    print("03_dual_axes.py: every assertion held.")


if __name__ == "__main__":
    main()
