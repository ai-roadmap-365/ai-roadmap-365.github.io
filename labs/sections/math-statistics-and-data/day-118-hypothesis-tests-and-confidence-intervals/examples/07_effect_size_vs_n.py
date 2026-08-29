"""Exercise 7 -- effect size versus significance.

The same relative difference -- a fixed 0.5% shift in the population mean
-- is tested at a small sample size and at an enormous one. At small n it
is not statistically significant; at huge n it is, reliably. The
underlying effect size never changed. Only the amount of data collected
around it did. "Statistically significant" is a statement about whether
noise can be ruled out, not about whether an effect is large enough to
matter.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
from inference import two_sample_z_test  # noqa: E402


def main() -> None:
    mean, sigma = ds.POP_MEAN, ds.POP_STD
    effect = mean * ds.EFFECT_VS_N_RELATIVE_DIFF
    cohens_d = effect / sigma

    print(f"Population mean: {mean}, population std: {sigma}")
    print(f"Fixed relative difference: {ds.EFFECT_VS_N_RELATIVE_DIFF:.1%}")
    print(f"Absolute effect size (population): {effect:.4f}")
    print(f"Standardized effect size (Cohen's d = effect/sigma): {cohens_d:.5f}")

    rng_small = np.random.default_rng(42)
    a_small = ds.normal_population(rng_small, ds.EFFECT_VS_N_SMALL_N, mean, sigma)
    b_small = ds.normal_population(rng_small, ds.EFFECT_VS_N_SMALL_N, mean + effect, sigma)
    _, p_small = two_sample_z_test(a_small, b_small)

    rng_large = np.random.default_rng(42)
    a_large = ds.normal_population(rng_large, ds.EFFECT_VS_N_LARGE_N, mean, sigma)
    b_large = ds.normal_population(rng_large, ds.EFFECT_VS_N_LARGE_N, mean + effect, sigma)
    _, p_large = two_sample_z_test(a_large, b_large)

    print(f"\nn={ds.EFFECT_VS_N_SMALL_N} per group: p = {p_small:.4f}")
    print(f"n={ds.EFFECT_VS_N_LARGE_N} per group: p = {p_large:.6f}")

    assert p_small > 0.05, f"expected the small-n case to be NOT significant, got p={p_small:.4f}"
    assert p_large < 0.05, f"expected the huge-n case to be significant, got p={p_large:.6f}"

    # The effect size itself -- the population parameter the two samples
    # were built around -- is a single fixed number, untouched by n.
    cohens_d_small = effect / sigma
    cohens_d_large = effect / sigma
    assert cohens_d_small == cohens_d_large == cohens_d, "the effect size is a population parameter, independent of n"

    print(
        "\nOK: the exact same 0.5% relative difference is not significant "
        f"at n={ds.EFFECT_VS_N_SMALL_N} and is significant at n={ds.EFFECT_VS_N_LARGE_N}. "
        "The effect size (Cohen's d) is identical in both cases -- only the "
        "power to detect it changed. A huge n can make a trivial difference "
        "'significant'; significance alone never tells you whether the "
        "difference is big enough to matter."
    )


if __name__ == "__main__":
    main()
