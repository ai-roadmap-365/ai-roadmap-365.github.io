"""Exercise 9: standardisation and z-scores. Standardising gives mean 0 and
standard deviation 1 by construction, and it does NOT change the Pearson
correlation between two variables."""

import numpy as np

import dataset as D
import descriptive as F


def main() -> None:
    rng = np.random.default_rng(D.STANDARDIZATION_SEED)
    x = rng.normal(D.STANDARDIZATION_X_MEAN, D.STANDARDIZATION_X_SIGMA, D.STANDARDIZATION_N)
    noise = rng.normal(0.0, D.STANDARDIZATION_Y_NOISE_SIGMA, D.STANDARDIZATION_N)
    y = D.STANDARDIZATION_Y_SLOPE * x + noise

    zx = F.zscores(x)
    zy = F.zscores(y)

    mean_zx = sum(zx) / len(zx)
    std_zx = (sum((v - mean_zx) ** 2 for v in zx) / len(zx)) ** 0.5
    print(f"standardised x: mean = {mean_zx:.2e}, std = {std_zx:.10f}")
    assert abs(mean_zx) < D.STANDARDIZATION_MEAN_TOLERANCE
    assert abs(std_zx - 1.0) < D.STANDARDIZATION_STD_TOLERANCE

    r_original = F.pearson(x, y)
    r_standardised = F.pearson(zx, zy)
    diff = abs(r_original - r_standardised)
    print(f"Pearson correlation, original x,y      = {r_original:.10f}")
    print(f"Pearson correlation, standardised x,y  = {r_standardised:.10f}")
    print(f"  difference                           = {diff:.2e}")
    assert diff < D.STANDARDIZATION_CORRELATION_TOLERANCE

    print()
    print(
        "Standardising rescaled every value's units, but it moved nothing "
        "relative to anything else -- correlation, which is exactly a "
        "statement about relative structure, could not have changed."
    )
    print("09_standardization.py: every assertion held.")


if __name__ == "__main__":
    main()
