"""Exercise 6 -- statistical power.

Power is P(reject H0 | H0 is false by a specific amount). It depends on
three things together: the true effect size, the sample size, and alpha.
"Found nothing" without a power figure is not evidence of absence -- it
might just mean the test never had a real chance to detect the effect
that was actually there.

This exercise computes power two ways: from the closed-form formula, and
by simulating the test itself thousands of times at a true effect size and
counting how often it actually rejects. The two must agree.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
from inference import power_two_sample_z, two_sample_z_test  # noqa: E402


def simulate_power(rng: np.random.Generator, effect: float, sigma: float, n: int, trials: int) -> float:
    rejections = 0
    for _ in range(trials):
        a = ds.normal_population(rng, n, ds.POP_MEAN, sigma)
        b = ds.normal_population(rng, n, ds.POP_MEAN + effect, sigma)
        _, p = two_sample_z_test(a, b)
        if p < 0.05:
            rejections += 1
    return rejections / trials


def main() -> None:
    sigma = ds.POP_STD

    # Power rises with n, at a fixed effect size.
    print(f"Power vs n, at a fixed effect of {ds.POWER_CHECK_EFFECT} (sigma={sigma}):")
    prev_power = -1.0
    for n in (10, 20, 50, 100, 200, 400):
        power = power_two_sample_z(ds.POWER_CHECK_EFFECT, sigma, n)
        print(f"  n={n:>4}: power={power:.4f}")
        assert power > prev_power, f"power should rise monotonically with n, failed at n={n}"
        prev_power = power

    # Power rises with effect size, at a fixed n.
    print(f"\nPower vs effect size, at a fixed n=100 (sigma={sigma}):")
    prev_power = -1.0
    for effect in (0.5, 1.0, 2.0, 4.0, 8.0):
        power = power_two_sample_z(effect, sigma, 100)
        print(f"  effect={effect:>4}: power={power:.4f}")
        assert power > prev_power, f"power should rise monotonically with effect size, failed at effect={effect}"
        prev_power = power

    # Check the formula against a direct simulation at one configuration.
    theoretical = power_two_sample_z(ds.POWER_CHECK_EFFECT, sigma, ds.POWER_CHECK_N)
    rng = np.random.default_rng(42)
    simulated = simulate_power(rng, ds.POWER_CHECK_EFFECT, sigma, ds.POWER_CHECK_N, ds.POWER_CHECK_TRIALS)
    print(
        f"\nConfiguration: effect={ds.POWER_CHECK_EFFECT}, n={ds.POWER_CHECK_N} per group, sigma={sigma}, alpha=0.05"
    )
    print(f"  theoretical power: {theoretical:.4f}")
    print(f"  simulated power ({ds.POWER_CHECK_TRIALS} trials): {simulated:.4f}")
    dev = abs(theoretical - simulated)
    assert dev <= ds.POWER_CHECK_TOLERANCE, (
        f"theoretical power {theoretical:.4f} and simulated power {simulated:.4f} "
        f"disagree by {dev:.4f}, more than the {ds.POWER_CHECK_TOLERANCE} tolerance"
    )

    print(
        "\nOK: power rises monotonically with both n and effect size, and "
        "the closed-form formula agrees with a direct simulation of the "
        "test itself."
    )


if __name__ == "__main__":
    main()
