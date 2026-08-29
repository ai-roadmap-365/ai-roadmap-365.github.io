"""Exercise 1 — the lie factor, implemented and measured.

Two bars. The same two numbers, 100 and 102, drawn twice: once on the
baseline matplotlib chooses for you, once on a baseline an author typed.
The shown ratio is read off the *rendered* bar geometry, never off the
input numbers, which is the only way the measurement means anything.
"""

import honesty as H

VALUES = (100.0, 102.0)


def main():
    print("Two bars, values 100 and 102. The data ratio is 102 / 100 = 1.02.")
    print()

    lf_honest, shown_honest, data_ratio = H.bar_pair_lie_factor(VALUES)
    print("  zero baseline (matplotlib's default for a bar chart)")
    print(f"    drawn height ratio : {shown_honest:.4f}")
    print(f"    data ratio         : {data_ratio:.4f}")
    print(f"    lie factor         : {lf_honest:.4f}")
    print()

    lf_lie, shown_lie, _ = H.bar_pair_lie_factor(VALUES, ylim=(99, 103))
    print("  y axis set to (99, 103) -- one line of code, no data changed")
    print(f"    drawn height ratio : {shown_lie:.4f}")
    print(f"    data ratio         : {data_ratio:.4f}")
    print(f"    lie factor         : {lf_lie:.4f}")
    print()

    assert abs(lf_honest - 1.0) < 1e-9, f"honest chart lie factor {lf_honest}"
    assert abs(shown_lie - 3.0) < 1e-9, f"truncated shown ratio {shown_lie}"
    assert lf_lie > 2.5, f"truncated lie factor {lf_lie}"

    print("  A two per cent difference, drawn as a bar three times as tall.")
    print(f"  Tufte's threshold for a distortion is a lie factor outside")
    print(f"  0.95 to 1.05. This one is {lf_lie:.2f}.")
    print()
    print("01_lie_factor.py: every assertion held.")


if __name__ == "__main__":
    main()
