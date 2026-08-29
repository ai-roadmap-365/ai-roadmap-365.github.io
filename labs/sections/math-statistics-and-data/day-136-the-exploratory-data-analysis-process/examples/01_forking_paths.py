"""Exercise 1 -- forking paths, measured.

An analyst with data that has NO real signal in it tries a few groupings,
a few subsets, a few outcome variables -- and after examining enough
combinations, one comes back "significant at p < 0.05". Nobody p-hacked.
Every individual test was computed correctly. This script measures the
exact size of that effect two ways: an exact formula for k independent
comparisons, and one concrete 40-comparison scan of a real (signal-free)
dataset with pandas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
import exploration as ex  # noqa: E402


def main() -> None:
    print("Part A -- the exact rate, confirmed by simulation, for k = 5, 20, 40")
    print()
    rng = np.random.default_rng(2026)
    for k in ds.FORK_K_VALUES:
        result = ex.simulate_forking_paths(rng, k, ds.FORK_FAMILIES, ds.FORK_N_PER_GROUP, ds.ALPHA)
        exact = result["exact_rate"]
        sim = result["simulated_rate"]
        se = result["standard_error"]
        dev = result["deviation"]
        print(
            f"  k={k:2d}: exact = 1 - (1-{ds.ALPHA})^{k} = {exact:.4f}   "
            f"simulated over {ds.FORK_FAMILIES} families = {sim:.4f}   "
            f"deviation = {dev:.4f} ({dev / se:.2f} SE)"
        )
        assert dev <= ds.FORK_SIM_TOLERANCE_SE * se, (
            f"k={k}: simulated {sim:.4f} is too far from exact {exact:.4f} "
            f"({dev / se:.2f} SE > {ds.FORK_SIM_TOLERANCE_SE} SE)"
        )
        expected_exact = {5: 0.2262, 20: 0.6415, 40: 0.8715}[k]
        assert abs(exact - expected_exact) < 0.0001, f"k={k}: expected exact~{expected_exact}, got {exact:.4f}"

    print()
    print("Part B -- one concrete dataset, forty real comparisons, no test declared")
    print("in advance for any of them")
    print()
    rng2 = np.random.default_rng(ds.NARRATIVE_SEED)
    df = ds.build_narrative_frame(rng2)
    results = ex.scan_narrative_frame(df, ds.NARRATIVE_SUBSET_COLS, ds.NARRATIVE_OUTCOME_COLS)
    n_comparisons = len(results)
    significant = [r for r in results if r["significant"]]
    print(f"  comparisons run: {n_comparisons}")
    print(f"  came back significant at alpha={ds.ALPHA}: {len(significant)}")
    assert n_comparisons >= ds.NARRATIVE_MIN_COMPARISONS, (
        f"expected at least {ds.NARRATIVE_MIN_COMPARISONS} comparisons, ran {n_comparisons}"
    )
    assert len(significant) >= 1, "expected at least one comparison to look significant by chance"

    best = ex.best_significant_result(results)
    print(
        f"  the 'winning' comparison: {best['subset']} x {best['outcome']} "
        f"({best['cut']}) -- p={best['p']:.4f}, effect size d={best['effect_size']:.3f}"
    )

    print(
        "\nOK: a p-value is only meaningful if you can say how many things "
        "you looked at. Twenty independent alpha=0.05 tests carry a 64.15% "
        "chance of at least one false positive; forty carry 87.15%; five "
        "still carry 22.62%. None of this requires bad faith -- it is what "
        "happens when chance gets enough tries, and one concrete forty-"
        "comparison scan of data with no real signal in it just produced "
        "exactly that."
    )


if __name__ == "__main__":
    main()
