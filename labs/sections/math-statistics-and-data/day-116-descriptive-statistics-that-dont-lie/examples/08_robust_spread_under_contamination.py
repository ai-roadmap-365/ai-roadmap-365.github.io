"""Exercise 8: robust spread under contamination. A few percent of extreme
values inflate the standard deviation dramatically and barely move the
median absolute deviation."""

import numpy as np

import dataset as D
import descriptive as F
import simulate as S


def main() -> None:
    rng = np.random.default_rng(D.CONTAMINATION_SEED)
    clean, contaminated = S.contaminated_sample(
        rng,
        D.CONTAMINATION_BASE_MEAN,
        D.CONTAMINATION_BASE_SIGMA,
        D.CONTAMINATION_BASE_N,
        D.CONTAMINATION_OUTLIERS,
    )
    contamination_fraction = len(D.CONTAMINATION_OUTLIERS) / len(contaminated)
    print(f"clean sample size        = {len(clean)}")
    print(f"outliers added           = {list(D.CONTAMINATION_OUTLIERS)}")
    print(f"contamination fraction   = {contamination_fraction:.1%}")

    std_clean = float(np.std(clean, ddof=1))
    std_contam = float(np.std(contaminated, ddof=1))
    std_multiplier = std_contam / std_clean
    print(f"standard deviation, clean        = {std_clean:.3f}")
    print(f"standard deviation, contaminated = {std_contam:.3f}")
    print(f"  multiplier                     = {std_multiplier:.2f}x")
    assert std_multiplier > D.CONTAMINATION_STD_MULTIPLIER_FLOOR

    mad_clean = F.median_absolute_deviation(clean)
    mad_contam = F.median_absolute_deviation(contaminated)
    mad_multiplier = mad_contam / mad_clean
    print(f"median absolute deviation, clean        = {mad_clean:.3f}")
    print(f"median absolute deviation, contaminated = {mad_contam:.3f}")
    print(f"  multiplier                            = {mad_multiplier:.2f}x")
    assert mad_multiplier < D.CONTAMINATION_MAD_MULTIPLIER_CEILING

    print()
    print(
        f"{contamination_fraction:.0%} contamination inflated the standard "
        f"deviation by {std_multiplier:.1f}x and the MAD by only "
        f"{mad_multiplier:.2f}x."
    )
    print("08_robust_spread_under_contamination.py: every assertion held.")


if __name__ == "__main__":
    main()
