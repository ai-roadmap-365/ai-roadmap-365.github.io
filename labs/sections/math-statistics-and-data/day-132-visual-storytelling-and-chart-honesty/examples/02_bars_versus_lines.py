"""Exercise 2 — truncation is fatal for bars and often fine for lines.

The same two numbers on the same non-zero baseline, drawn two ways. The
bar version's lie factor is nearly three. The line version's is exactly
one. The difference is not taste; it is what each mark encodes.
"""

import honesty as H

VALUES = (100.0, 102.0)
YLIM = (99, 103)


def main():
    lf_bar, shown_bar, ratio = H.bar_pair_lie_factor(VALUES, ylim=YLIM)
    lf_line, shown_change, true_change = H.line_pair_lie_factor(VALUES, ylim=YLIM)
    lf_line_zero, _, _ = H.line_pair_lie_factor(VALUES)

    print(f"Values {VALUES[0]:.0f} and {VALUES[1]:.0f}, y axis {YLIM}, two encodings.")
    print()
    print("  BAR -- encodes value as length from the baseline")
    print(f"    shown length ratio : {shown_bar:.4f}   (true ratio {ratio:.4f})")
    print(f"    lie factor         : {lf_bar:.4f}")
    print()
    print("  LINE -- encodes change as vertical displacement")
    print(f"    shown change       : {shown_change:.4f}   (true change {true_change:.4f})")
    print(f"    lie factor         : {lf_line:.4f}")
    print(f"    same line on a zero baseline, lie factor: {lf_line_zero:.4f}")
    print()

    assert lf_bar > 2.5, f"bar lie factor {lf_bar}"
    assert abs(lf_line - 1.0) < 1e-9, f"line lie factor {lf_line}"
    assert abs(lf_line_zero - 1.0) < 1e-9, f"line lie factor on zero {lf_line_zero}"

    print("  Cutting the axis destroys a bar's encoding, because the bar's")
    print("  length IS the value. It leaves a line's encoding untouched,")
    print("  because a labelled linear axis still converts displacement back")
    print("  to the true change -- whatever the baseline is.")
    print()
    print("  The rule that follows: a non-zero baseline is legitimate for a")
    print("  line and never for a bar, and either way the baseline must be")
    print("  visible and labelled.")
    print()
    print("02_bars_versus_lines.py: every assertion held.")


if __name__ == "__main__":
    main()
