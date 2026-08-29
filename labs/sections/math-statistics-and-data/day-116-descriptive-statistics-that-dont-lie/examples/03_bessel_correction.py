"""Exercise 3: Bessel's correction, measured rather than asserted.

Draw many samples of size 5 from a population of known variance. The
divide-by-n estimator should be biased LOW by the factor (n-1)/n on
average; the divide-by-(n-1) estimator should be unbiased, within a few
standard errors of its own sampling mean.
"""

import numpy as np

import dataset as D
import simulate as S


def main() -> None:
    rng = np.random.default_rng(D.BESSEL_SEED)
    biased, unbiased = S.bessel_trial_variances(
        rng,
        D.BESSEL_POPULATION_MEAN,
        D.BESSEL_POPULATION_SIGMA,
        D.BESSEL_SAMPLE_SIZE,
        D.BESSEL_TRIALS,
    )

    print(f"true population variance        = {D.BESSEL_TRUE_VARIANCE}")
    print(f"sample size (n)                 = {D.BESSEL_SAMPLE_SIZE}")
    print(f"trials                          = {D.BESSEL_TRIALS:,}")

    mean_biased = float(biased.mean())
    ratio_biased = mean_biased / D.BESSEL_TRUE_VARIANCE
    print(f"mean of divide-by-n estimator   = {mean_biased:.4f}")
    print(f"  ratio to true variance        = {ratio_biased:.4f}")
    print(f"  predicted ratio (n-1)/n       = {D.BESSEL_EXPECTED_BIAS_FACTOR:.4f}")
    assert abs(ratio_biased - D.BESSEL_EXPECTED_BIAS_FACTOR) < D.BESSEL_BIAS_FACTOR_TOLERANCE

    mean_unbiased = float(unbiased.mean())
    se_unbiased = float(unbiased.std(ddof=1)) / (D.BESSEL_TRIALS**0.5)
    deviations_in_se = abs(mean_unbiased - D.BESSEL_TRUE_VARIANCE) / se_unbiased
    print(f"mean of divide-by-(n-1) estimator = {mean_unbiased:.4f}")
    print(f"  standard error of that mean     = {se_unbiased:.4f}")
    print(f"  distance from truth, in SEs     = {deviations_in_se:.2f}")
    assert deviations_in_se < D.BESSEL_UNBIASED_SE_TOLERANCE

    print(
        f"Dividing by n underestimates the true variance by a factor of "
        f"~{1 - ratio_biased:.1%}. Dividing by n-1 lands within "
        f"{deviations_in_se:.2f} standard errors of the truth."
    )
    print("03_bessel_correction.py: every assertion held.")


if __name__ == "__main__":
    main()
