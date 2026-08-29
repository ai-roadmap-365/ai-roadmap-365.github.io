"""Exercise 3 -- the test/interval duality.

A two-sided hypothesis test at level alpha rejects the null value exactly
when the (1 - alpha) confidence interval excludes it. Same underlying
machinery (the same z, the same standard error), presented two ways. This
is not a coincidence to be approximated -- it should hold EXACTLY, dataset
by dataset, because both are built from the identical z statistic.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
from inference import ci_excludes, confidence_interval_mean, one_sample_z_test_against_value  # noqa: E402


def main() -> None:
    rng = np.random.default_rng(7)
    n_datasets = 2000
    alpha = 0.05
    null_value = ds.POP_MEAN
    mismatches = 0
    rejections = 0

    for _ in range(n_datasets):
        n = int(rng.integers(15, 80))
        # Half the datasets are centred at the null value, half are shifted,
        # so both a "reject" and a "fail to reject" outcome actually occur.
        shift = 0.0 if rng.random() < 0.5 else rng.uniform(-6.0, 6.0)
        sample = ds.normal_population(rng, n, ds.POP_MEAN + shift, ds.POP_STD)

        _, p = one_sample_z_test_against_value(sample, null_value)
        rejects = p < alpha
        if rejects:
            rejections += 1

        interval = confidence_interval_mean(sample, alpha)
        excludes = ci_excludes(interval, null_value)

        if rejects != excludes:
            mismatches += 1

    print(f"Datasets checked: {n_datasets}")
    print(f"Test rejected the null in {rejections} of them")
    print(f"Test/interval disagreements: {mismatches}")

    assert mismatches == 0, (
        f"the test and the interval disagreed on {mismatches} of {n_datasets} "
        "datasets -- they should never disagree, since both come from the same z"
    )
    assert 0 < rejections < n_datasets, "the mix of shifted and unshifted datasets should produce both outcomes"

    print(
        "OK: across every dataset, rejecting at alpha and the interval "
        "excluding the null value agreed exactly -- zero mismatches."
    )


if __name__ == "__main__":
    main()
