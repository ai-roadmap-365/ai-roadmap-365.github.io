"""Exercise 4 -- choices are comparisons.

"I only ran one test" is not a defence if you tried several subset filters
or several outcome definitions and reported whichever cut looked best,
even if you never typed the word "test" for the others. This script
builds data with NO real signal, varies a recency cutoff (five values) and
an outcome definition (two variants) -- ten variants total, with no
explicit test declared per variant -- and measures how often the single
best-looking cell of that grid comes back "significant" at alpha=0.05,
compared with how often ONE pre-declared comparison does.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
import exploration as ex  # noqa: E402


def main() -> None:
    rng = np.random.default_rng(ds.CHOICES_SEED)

    # One concrete illustration first.
    df = ex.build_choices_frame(rng, ds.CHOICES_N_ROWS)
    best = ex.best_of_choice_grid(df, ds.CHOICES_SUBSET_CUTOFFS, ds.CHOICES_OUTCOME_DEFINITIONS)
    n_variants = len(ds.CHOICES_SUBSET_CUTOFFS) * len(ds.CHOICES_OUTCOME_DEFINITIONS)
    print(f"One dataset, {n_variants} silent variants (cutoff x outcome definition), best cell:")
    print(f"  cutoff={best['cutoff']} days, outcome='{best['definition']}' -> z={best['z']:.3f} p={best['p']:.4f}")

    # Now the rate, under a TRUE null, across many such datasets.
    print(f"\nMeasuring across {ds.CHOICES_FAMILIES} independently generated null datasets...")
    result = ex.simulate_choice_grid_best_p_rate(
        rng, ds.CHOICES_FAMILIES, ds.CHOICES_N_ROWS,
        ds.CHOICES_SUBSET_CUTOFFS, ds.CHOICES_OUTCOME_DEFINITIONS, ds.ALPHA
    )
    print(f"  best-of-{result['n_variants']}-silent-variants 'significant' rate: {result['naive_best_rate']:.4f}")
    print(f"  one pre-declared comparison 'significant' rate: {result['single_declared_rate']:.4f}")

    assert result["naive_best_rate"] > 3 * ds.ALPHA, (
        f"expected the best-of-grid rate to be well above the nominal alpha={ds.ALPHA}, "
        f"got {result['naive_best_rate']:.4f}"
    )
    assert abs(result["single_declared_rate"] - ds.ALPHA) < 0.02, (
        f"the single pre-declared comparison should sit near alpha={ds.ALPHA}, "
        f"got {result['single_declared_rate']:.4f}"
    )

    inflation = result["naive_best_rate"] / result["single_declared_rate"]
    print(
        f"\nOK: no test was declared per variant -- just 'try a few cutoffs "
        f"and a couple of outcome definitions, report the one that looks "
        f"best.' That silent search inflates the apparent significance "
        f"rate by roughly {inflation:.1f}x over one pre-declared comparison, "
        "on data with no real signal in it at all. A choice about which "
        "subset or which outcome definition to use IS a comparison, "
        "counted or not."
    )


if __name__ == "__main__":
    main()
