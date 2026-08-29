"""Exercise 9 -- bootstrap interval versus the normal-approximation interval.

Day 117 built the bootstrap from scratch: resample with replacement,
recompute the statistic, read the spread. Today's normal-approximation
interval (mean +/- z * standard_error) is a closed-form shortcut that is
valid under the same conditions the CLT needs. Where both are valid --
here, the mean of a reasonably-sized sample from a well-behaved
population -- they should agree closely, without needing to be identical.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
from inference import bootstrap_ci, confidence_interval_mean  # noqa: E402


def main() -> None:
    rng = np.random.default_rng(42)
    n = 200
    sample = ds.normal_population(rng, n, ds.POP_MEAN, ds.POP_STD)

    normal_lo, normal_hi = confidence_interval_mean(sample, alpha=0.05)
    boot_lo, boot_hi = bootstrap_ci(sample, np.mean, ds.BOOTSTRAP_N_BOOT, 0.05, rng)

    normal_center = (normal_lo + normal_hi) / 2
    boot_center = (boot_lo + boot_hi) / 2
    normal_width = normal_hi - normal_lo
    boot_width = boot_hi - boot_lo
    se = sample.std(ddof=1) / np.sqrt(n)

    print(f"Sample: n={n}, mean={sample.mean():.4f}, std={sample.std(ddof=1):.4f}, SE={se:.4f}")
    print(f"Normal-approximation 95% CI:  [{normal_lo:.4f}, {normal_hi:.4f}]  width={normal_width:.4f}")
    print(f"Bootstrap ({ds.BOOTSTRAP_N_BOOT} resamples) 95% CI: [{boot_lo:.4f}, {boot_hi:.4f}]  "
          f"width={boot_width:.4f}")

    center_diff_in_se = abs(normal_center - boot_center) / se
    width_ratio = boot_width / normal_width
    print(f"Center difference: {center_diff_in_se:.4f} standard errors")
    print(f"Width ratio (bootstrap/normal): {width_ratio:.4f}")

    assert center_diff_in_se <= ds.BOOTSTRAP_CENTER_TOLERANCE_IN_SE, (
        f"centers differ by {center_diff_in_se:.4f} SE, more than the "
        f"{ds.BOOTSTRAP_CENTER_TOLERANCE_IN_SE} SE tolerance"
    )
    assert abs(width_ratio - 1.0) <= ds.BOOTSTRAP_WIDTH_RATIO_TOLERANCE, (
        f"width ratio {width_ratio:.4f} is more than "
        f"{ds.BOOTSTRAP_WIDTH_RATIO_TOLERANCE} away from 1.0"
    )

    print(
        "\nOK: the bootstrap interval and the normal-approximation interval "
        "agree closely where both are valid -- the bootstrap needed no "
        "formula for the standard error of the mean, and would work exactly "
        "the same way for a statistic that has no such formula."
    )


if __name__ == "__main__":
    main()
