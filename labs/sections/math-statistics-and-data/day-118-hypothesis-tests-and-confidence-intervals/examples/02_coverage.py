"""Exercise 2 -- the centrepiece. What does "95% confidence" actually mean?

Build 10,000 nominal-95% confidence intervals from independent samples of a
population with a KNOWN true mean, and count how many of them actually
contain it. If the textbook claim is right, about 95% will -- not because
any one interval has a 95% chance of containing the fixed true mean (a
fixed number either is or is not in a fixed interval), but because the
PROCEDURE that builds the interval catches the true value 95% of the time
across repetition.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
from inference import confidence_interval_mean  # noqa: E402


def measure_coverage(rng: np.random.Generator, trials: int, n: int) -> float:
    hits = 0
    for _ in range(trials):
        sample = ds.normal_population(rng, n, ds.POP_MEAN, ds.POP_STD)
        lo, hi = confidence_interval_mean(sample, alpha=0.05)
        if lo <= ds.POP_MEAN <= hi:
            hits += 1
    return hits / trials


def main() -> None:
    rng = np.random.default_rng(42)
    coverage = measure_coverage(rng, ds.COVERAGE_TRIALS, ds.COVERAGE_SAMPLE_N)

    print(f"True population mean: {ds.POP_MEAN}")
    print(f"Nominal confidence level: {ds.COVERAGE_TARGET:.0%}")
    print(f"Intervals built: {ds.COVERAGE_TRIALS}")
    print(f"Measured coverage: {coverage:.4f}")
    print(f"Standard error of the measured coverage: {ds.COVERAGE_SE:.5f}")
    print(f"3-SE tolerance band: [{ds.COVERAGE_TARGET - ds.COVERAGE_TOLERANCE:.4f}, "
          f"{ds.COVERAGE_TARGET + ds.COVERAGE_TOLERANCE:.4f}]")

    deviation = abs(coverage - ds.COVERAGE_TARGET)
    assert deviation <= ds.COVERAGE_TOLERANCE, (
        f"measured coverage {coverage:.4f} is more than 3 SE "
        f"({ds.COVERAGE_TOLERANCE:.4f}) away from the nominal {ds.COVERAGE_TARGET:.2f}"
    )

    print(
        "OK: measured coverage is within three standard errors of the nominal "
        "95%. This IS the definition of a confidence interval -- not a claim "
        "about any one interval, a measured property of the procedure."
    )


if __name__ == "__main__":
    main()
