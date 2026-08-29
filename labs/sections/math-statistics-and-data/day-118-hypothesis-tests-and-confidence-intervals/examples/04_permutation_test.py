"""Exercise 4 -- the permutation test, from scratch.

No distributional assumption: shuffle the group labels, recompute the
statistic, repeat thousands of times, and read the p-value off how often a
shuffle produced something at least as extreme as what was actually
observed. Building this makes the meaning of "p-value" concrete in a way
a formula does not: it is a literal count of how surprising the real
arrangement was among all the ways the labels could have fallen.

Two cases:
  1. Two roughly normal populations at a moderate n, where the z-test's
     normal approximation is solid -- the two methods should land close.
  2. Two heavily right-skewed populations at a small n, where the normal
     approximation is shakier -- the two methods diverge more, and the
     permutation test needs no assumption about the population's shape to
     stay valid.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
from inference import permutation_test_diff_means, two_sample_z_test  # noqa: E402


def main() -> None:
    # Two independent generators, one per case, so neither case's random
    # draws depend on how many numbers the other case happened to consume.
    rng_case1 = np.random.default_rng(1)
    rng_case2 = np.random.default_rng(1)

    # Case 1: moderate n, normal populations -- the approximation should hold.
    a = ds.normal_population(rng_case1, 60, ds.POP_MEAN, ds.POP_STD)
    b = ds.normal_population(rng_case1, 60, ds.POP_B_MEAN, ds.POP_B_STD)
    z, p_z = two_sample_z_test(a, b)
    observed, p_perm = permutation_test_diff_means(a, b, 5000, rng_case1)
    print("Case 1 -- normal populations, n=60 each:")
    print(f"  observed difference in means: {observed:.4f}")
    print(f"  z-test p-value:          {p_z:.4f}")
    print(f"  permutation-test p-value: {p_perm:.4f}")
    diff_case1 = abs(p_z - p_perm)
    print(f"  |difference|: {diff_case1:.4f}")
    assert diff_case1 < 0.03, "at n=60 with normal populations, the two methods should agree closely"

    # Case 2: small n, right-skewed populations -- the normal approximation
    # is on shakier ground; the permutation test does not need it at all.
    c = ds.skewed_population(rng_case2, 8)
    d = ds.skewed_population(rng_case2, 8)
    z2, p_z2 = two_sample_z_test(c, d)
    observed2, p_perm2 = permutation_test_diff_means(c, d, 5000, rng_case2)
    print("\nCase 2 -- right-skewed populations, n=8 each:")
    print(f"  observed difference in means: {observed2:.4f}")
    print(f"  z-test p-value:          {p_z2:.4f}")
    print(f"  permutation-test p-value: {p_perm2:.4f}")
    diff_case2 = abs(p_z2 - p_perm2)
    print(f"  |difference|: {diff_case2:.4f}")
    # Both p-values must be sane probabilities, and the point of this case
    # is that they are allowed to diverge more than in Case 1 -- the
    # permutation test does not owe the normal approximation any agreement.
    assert 0.0 <= p_z2 <= 1.0 and 0.0 <= p_perm2 <= 1.0
    assert diff_case2 > diff_case1, (
        "the small-n, skewed case should show the two methods diverging "
        "more than the moderate-n, normal case did"
    )

    print(
        "\nOK: the permutation test agrees closely with the z-test where "
        "the normal approximation is solid, and diverges more where it is "
        "not -- while remaining a valid probability in both cases."
    )


if __name__ == "__main__":
    main()
