"""Exercise 8 -- peeking, the most common real sin.

A test's alpha (say 5%) is a promise about ONE look at ONE fixed sample
size. Checking the p-value after every batch of new data and stopping the
instant it dips below 0.05 is a different procedure entirely -- and its
real false-positive rate is far higher than 5%, even though every single
p-value computed along the way was calculated correctly.

This simulates many independent "experiments" under a population where
the null hypothesis is TRUE (mean exactly 0), each one collecting data in
batches of 10 and stopping at the first p < 0.05, and measures how often
that early stop happens purely from noise.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
from inference import one_sample_z_test_against_value  # noqa: E402


def run_experiment(rng: np.random.Generator) -> bool:
    """Returns True if peeking produced a false positive on this experiment."""
    data: list[float] = []
    for _ in range(ds.PEEK_MAX_BATCHES):
        data.extend(rng.normal(0.0, 1.0, ds.PEEK_BATCH_SIZE).tolist())
        arr = np.array(data)
        _, p = one_sample_z_test_against_value(arr, 0.0)
        if p < ds.PEEK_ALPHA:
            return True
    return False


def fixed_n_false_positive_rate(rng: np.random.Generator, n: int, trials: int) -> float:
    """The honest comparison: test ONCE at a fixed final sample size."""
    false_positives = 0
    for _ in range(trials):
        arr = rng.normal(0.0, 1.0, n)
        _, p = one_sample_z_test_against_value(arr, 0.0)
        if p < ds.PEEK_ALPHA:
            false_positives += 1
    return false_positives / trials


def main() -> None:
    rng = np.random.default_rng(42)
    peeked_false_positives = sum(run_experiment(rng) for _ in range(ds.PEEK_EXPERIMENTS))
    peeked_rate = peeked_false_positives / ds.PEEK_EXPERIMENTS

    final_n = ds.PEEK_BATCH_SIZE * ds.PEEK_MAX_BATCHES
    fixed_rate = fixed_n_false_positive_rate(rng, final_n, ds.PEEK_EXPERIMENTS)

    print(f"True null hypothesis (population mean is exactly 0), alpha={ds.PEEK_ALPHA}")
    print(f"Experiments simulated: {ds.PEEK_EXPERIMENTS}")
    print(f"Looks per experiment: {ds.PEEK_MAX_BATCHES} (every {ds.PEEK_BATCH_SIZE} observations, "
          f"up to n={final_n})")
    print(f"\nFalse-positive rate WITH peeking (stop at first p<0.05): {peeked_rate:.4f}")
    print(f"False-positive rate testing ONCE at n={final_n} (honest, no peeking): {fixed_rate:.4f}")
    print(f"Inflation factor: {peeked_rate / ds.PEEK_ALPHA:.2f}x nominal alpha")

    assert peeked_rate >= ds.PEEK_ALPHA * ds.PEEK_MIN_INFLATION_FACTOR, (
        f"peeking false-positive rate {peeked_rate:.4f} should be at least "
        f"{ds.PEEK_MIN_INFLATION_FACTOR}x alpha ({ds.PEEK_ALPHA * ds.PEEK_MIN_INFLATION_FACTOR:.4f})"
    )
    assert abs(fixed_rate - ds.PEEK_ALPHA) < 0.02, (
        f"the honest fixed-n rate {fixed_rate:.4f} should sit close to alpha={ds.PEEK_ALPHA}"
    )
    assert peeked_rate > fixed_rate, "peeking must produce a higher false-positive rate than the honest fixed-n test"

    print(
        "\nOK: testing repeatedly and stopping at the first p<0.05 inflates "
        "the true false-positive rate several times past the nominal alpha, "
        "even though every individual p-value was computed correctly and the "
        "null hypothesis was true the entire time. The fix is deciding the "
        "sample size in advance (or using a sequential-testing method built "
        "for repeated looks), not testing whenever the data happens to look "
        "promising."
    )


if __name__ == "__main__":
    main()
