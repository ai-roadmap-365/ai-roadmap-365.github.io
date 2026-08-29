"""Exercise 5 -- multiple comparisons and the Bonferroni correction.

A team that checks twenty independent metrics at alpha = 0.05 and calls
anything under 0.05 "significant" is not running one 5%-error test. It is
running a FAMILY of twenty tests, and the chance that at least one comes
back "significant" under pure noise is 1 - 0.95**20 -- an exact number,
derived below, confirmed by simulation, and then pulled back down with a
Bonferroni correction.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
from inference import bonferroni_alpha, z_critical_two_sided  # noqa: E402


def main() -> None:
    # --- The exact analytic value ---
    exact = 1 - (1 - ds.FWER_ALPHA) ** ds.FWER_TRIALS
    print(f"P(at least one false positive among {ds.FWER_TRIALS} independent "
          f"alpha={ds.FWER_ALPHA} tests) = 1 - (1-{ds.FWER_ALPHA})^{ds.FWER_TRIALS} "
          f"= {exact:.4f}")
    assert abs(exact - 0.6415) < 0.0001, f"expected 0.6415, got {exact:.4f}"

    # --- Confirm by simulation: many "families" of 20 independent tests
    # under a TRUE null (standard normal z-statistics), count how often at
    # least one exceeds the uncorrected critical value. ---
    rng = np.random.default_rng(42)
    z_crit = z_critical_two_sided(ds.FWER_ALPHA)
    at_least_one = 0
    for _ in range(ds.FWER_FAMILIES):
        zs = rng.standard_normal(ds.FWER_TRIALS)
        if np.any(np.abs(zs) > z_crit):
            at_least_one += 1
    simulated_fwer = at_least_one / ds.FWER_FAMILIES
    print(f"Simulated over {ds.FWER_FAMILIES} families: {simulated_fwer:.4f}")
    dev = abs(simulated_fwer - exact)
    assert dev <= ds.FWER_SIM_TOLERANCE, (
        f"simulated FWER {simulated_fwer:.4f} is too far from the exact "
        f"value {exact:.4f} (deviation {dev:.4f} > tolerance {ds.FWER_SIM_TOLERANCE})"
    )

    # --- Bonferroni: use alpha/m per test instead of alpha, and the
    # family-wise rate falls back down near the nominal alpha. ---
    corrected_alpha = bonferroni_alpha(ds.FWER_ALPHA, ds.FWER_TRIALS)
    print(f"Bonferroni-corrected per-test alpha: {ds.FWER_ALPHA}/{ds.FWER_TRIALS} = {corrected_alpha:.4f}")
    z_crit_corrected = z_critical_two_sided(corrected_alpha)
    at_least_one_corrected = 0
    for _ in range(ds.FWER_FAMILIES):
        zs = rng.standard_normal(ds.FWER_TRIALS)
        if np.any(np.abs(zs) > z_crit_corrected):
            at_least_one_corrected += 1
    simulated_bonferroni = at_least_one_corrected / ds.FWER_FAMILIES
    print(f"Simulated family-wise rate WITH Bonferroni: {simulated_bonferroni:.4f}")
    print(f"Analytic Bonferroni family-wise rate: {ds.BONFERRONI_EXPECTED:.4f}")
    dev_bonf = abs(simulated_bonferroni - ds.BONFERRONI_EXPECTED)
    assert dev_bonf <= ds.BONFERRONI_TOLERANCE, (
        f"Bonferroni-corrected simulated rate {simulated_bonferroni:.4f} is too far "
        f"from the analytic {ds.BONFERRONI_EXPECTED:.4f}"
    )
    assert abs(ds.BONFERRONI_EXPECTED - 0.0488) < 0.001, f"expected ~0.0488, got {ds.BONFERRONI_EXPECTED:.4f}"

    print(
        "\nOK: twenty uncorrected alpha=0.05 tests give a 64% chance of at "
        "least one false positive, confirmed by simulation. Bonferroni "
        "(alpha/m per test) pulls the family-wise rate back to about 4.9%. "
        "Most p-hacking is exactly this mechanism run silently, not fraud."
    )


if __name__ == "__main__":
    main()
