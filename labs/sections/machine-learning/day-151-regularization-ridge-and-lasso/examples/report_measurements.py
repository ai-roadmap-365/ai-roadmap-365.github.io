#!/usr/bin/env python3
"""Print every measured pair in this lab as one table.

The harness compares this output byte for byte against
expected-output/measured-values.txt, so the report is not a convenience:
it is how the lab notices that a number in the lesson has gone stale.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import regularization_lib as r  # noqa: E402

ALPHA_GRID = [0.001, 0.01, 0.1, 1.0]
PATH_ALPHAS = np.logspace(-3, 2, 60)


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 151 -- regularization: ridge and lasso, measured")
    print("=" * 54)

    rule("1. Ridge never zeros; lasso zeros progressively more")
    print("   alpha   lasso-zeros   lasso-R2   ridge-zeros   ridge-R2")
    for alpha, lz, lr2, rz, rr2 in r.zero_counts_and_r2(ALPHA_GRID):
        print(f"  {alpha:6.3f}       {lz}/10      {lr2:.4f}        {rz}/10      {rr2:.4f}")

    rule("1b. LassoCV picks its own alpha")
    cv = r.lasso_cv_selection()
    print(f"  alpha={cv['alpha']:.5f}  zeros={cv['zeros']}/10  test R2={cv['r2']:.4f}")
    print(f"  kept: {cv['kept']}")

    rule("2. The coefficient path: where each lasso coefficient hits zero")
    zero_at, ridge_ever_zero = r.alpha_where_each_lasso_coefficient_first_hits_zero(PATH_ALPHAS)
    for name in r.FEATURE_NAMES:
        print(f"  {name:4s} zeros at alpha = {zero_at[name]:.4f}")
    print(f"  ridge ever zero across the same 60-point sweep: {ridge_ever_zero}")

    rule("3. Does lasso recover the RIGHT features? A known sparse truth")
    p1, r1, n1 = r.sparse_recovery(alpha=1.0, noise=1.0, seed=0)
    print(f"  alpha=1.0  noise=1.0   precision={p1:.4f}  recall={r1:.4f}  n_selected={n1}")
    p2, r2v, n2 = r.sparse_recovery(alpha=80.0, noise=30.0, seed=0)
    print(f"  alpha=80.0 noise=30.0  precision={p2:.4f}  recall={r2v:.4f}  n_selected={n2}")
    p3, r3, n3 = r.sparse_recovery(alpha=80.0, noise=10.0, seed=0)
    print(f"  alpha=80.0 noise=10.0  precision={p3:.4f}  recall={r3:.4f}  n_selected={n3}")
    mp_low, mr_low = r.sparse_recovery_across_seeds(alpha=1.0, noise=1.0)
    mp_high, mr_high = r.sparse_recovery_across_seeds(alpha=1.0, noise=10.0)
    print(f"  mean over 10 seeds, alpha=1.0 noise=1.0  : precision={mp_low:.4f}  recall={mr_low:.4f}")
    print(f"  mean over 10 seeds, alpha=1.0 noise=10.0 : precision={mp_high:.4f}  recall={mr_high:.4f}")

    rule("4. Regularization requires scaled features")
    scale = r.scale_dependence(alpha=1.0)
    for label in ("raw", "standardized", "sklearn_unit_norm"):
        print(f"  {label:18s} n_kept={scale[label]['n_kept']:2d}  kept={scale[label]['kept']}")

    rule("5. ElasticNet interpolates between ridge and lasso")
    print("  l1_ratio   zeros   R2")
    for l1_ratio, zeros, r2v in r.elasticnet_sweep(alpha=0.1, l1_ratios=[0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]):
        print(f"  {l1_ratio:6.1f}      {zeros}/10   {r2v:.4f}")

    rule("5b. Ridge and ElasticNet do not share an alpha scale")
    ridge_head, elastic_head, max_diff = r.ridge_elasticnet_equivalence(alpha=0.1)
    print(f"  Ridge(alpha=0.1 * n_train) coefs[:3]        : {ridge_head}")
    print(f"  ElasticNet(alpha=0.1, l1_ratio=0) coefs[:3] : {elastic_head}")
    print(f"  max abs difference after the n_train correction: {max_diff:.4f}")

    rule("6. Correlated predictors: ridge splits, lasso picks one")
    _X, _y, correlation = r.near_duplicate_dataset()
    print(f"  correlation between the two near-duplicate columns: {correlation:.6f}")
    for alpha, ridge_coefs, lasso_coefs in r.ridge_vs_lasso_on_duplicates([0.001, 0.1, 1.0, 10.0]):
        print(f"  alpha={alpha:6.3f}  ridge={ridge_coefs}  lasso={lasso_coefs}")

    rule("7. Ridge has a closed form; lasso needs iterations")
    info = r.ridge_has_no_iteration_count()
    print(f"  ridge solver: {info['ridge_solver']}  ridge has n_iter_: {info['ridge_has_n_iter']}")
    print(f"  lasso has n_iter_: {info['lasso_has_n_iter']}")
    counts = r.lasso_iteration_counts(ALPHA_GRID)
    for alpha, n_iter in counts.items():
        print(f"  lasso alpha={alpha:<6} n_iter_={n_iter}")

    rule("8. The corner: two correlated features, small enough to see it")
    ols, rows = r.two_feature_corner_demo([0.001, 0.5, 1.0, 3.0, 8.0])
    print(f"  OLS coefficients (no penalty): {ols}")
    for alpha, ridge_coefs, lasso_coefs in rows:
        print(f"  alpha={alpha:6.3f}  ridge={ridge_coefs}  lasso={lasso_coefs}")


if __name__ == "__main__":
    main()
