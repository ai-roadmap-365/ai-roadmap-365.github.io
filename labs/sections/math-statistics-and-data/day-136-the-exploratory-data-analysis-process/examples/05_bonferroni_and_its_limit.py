"""Exercise 5 -- Bonferroni, and its honest limit.

Bonferroni (Day 118) works when you can COUNT your comparisons: dividing
alpha by the known number of tests, m, restores the family-wise error
rate to near its nominal level. The deeper problem is that in real
exploration you usually cannot count them -- every subset filter, cutoff
and outcome definition tried and discarded was a comparison too (exercise
4), and most of them never got written down. This script shows both
halves honestly: the correction working when m is known, and the same
correction failing -- not gracefully, not a little, but by a wide margin
-- when the number an analyst actually tried is larger than the number
they reported.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
import exploration as ex  # noqa: E402


def main() -> None:
    rng = np.random.default_rng(5)

    known_m = ds.BONFERRONI_KNOWN_M
    corrected_alpha = ex.bonferroni_alpha(ds.ALPHA, known_m)
    print(f"Reported (and true) comparison count: m={known_m}")
    print(f"Bonferroni-corrected per-test alpha: {ds.ALPHA}/{known_m} = {corrected_alpha:.5f}")

    rate_when_m_is_right = ex.simulate_family_wise_rate(rng, known_m, ds.BONFERRONI_FAMILIES, corrected_alpha)
    print(f"Family-wise rate when m is correctly known: {rate_when_m_is_right:.4f} (target ~ {ds.ALPHA})")
    assert abs(rate_when_m_is_right - ds.ALPHA) < 0.015, (
        f"expected the corrected rate to sit near alpha={ds.ALPHA}, got {rate_when_m_is_right:.4f}"
    )

    true_m = ds.BONFERRONI_TRUE_M
    print(f"\nNow suppose the analyst actually tried {true_m} comparisons before landing on the")
    print(f"{known_m} they wrote down, and applied the SAME corrected alpha ({corrected_alpha:.5f})")
    print("computed from the reported count, not the true one:")
    rate_when_m_is_wrong = ex.simulate_family_wise_rate(rng, true_m, ds.BONFERRONI_FAMILIES, corrected_alpha)
    print(f"Family-wise rate with the wrong m: {rate_when_m_is_wrong:.4f}")

    assert rate_when_m_is_wrong > 2 * ds.ALPHA, (
        f"expected the mis-corrected rate to substantially exceed alpha={ds.ALPHA}, "
        f"got {rate_when_m_is_wrong:.4f}"
    )
    assert rate_when_m_is_wrong > rate_when_m_is_right, "the wrong-m rate must exceed the correct-m rate"

    print(
        f"\nOK: with m known and reported honestly, Bonferroni pulls the "
        f"family-wise rate back to {rate_when_m_is_right:.4f}, close to the "
        f"nominal {ds.ALPHA}. Apply the identical correction computed for "
        f"m={known_m} to a search that actually ran m={true_m} comparisons, "
        f"and the real rate is {rate_when_m_is_wrong:.4f} -- roughly "
        f"{rate_when_m_is_wrong / ds.ALPHA:.1f} times the nominal alpha. "
        "The correction is not wrong; the count fed into it was. This is "
        "why the research log (exercise 6) matters more than the formula: "
        "Bonferroni cannot rescue a comparison count nobody kept."
    )


if __name__ == "__main__":
    main()
