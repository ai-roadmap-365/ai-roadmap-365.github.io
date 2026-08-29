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

import fitting_lib as f  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 145 -- overfitting and underfitting, decomposed and measured")
    print("=" * 63)
    print()
    print(f"  The data is a cubic plus Gaussian noise of standard deviation {f.NOISE_SD}.")
    print(f"  So no model of any capacity can score below {f.irreducible_variance():.4f}.")

    rule("1. The capacity sweep: 25 training rows, 2000 test rows")
    degrees = [1, 2, 3, 4, 6, 8, 10, 14, 18, 24]
    rows = f.capacity_sweep(degrees)
    print("   deg    train MSE        test MSE             gap")
    for degree, train, test, gap in rows:
        print(f"  {degree:4d}   {train:10.4f}   {test:13.4f}   {gap:13.4f}")
    print(f"  lowest test error at degree {f.best_degree(rows)}")
    train_column = [row[1] for row in rows]
    print(f"  training error falls at every step through degree 14 : "
          f"{f.is_monotonically_decreasing(train_column[:8])}")
    print("  after that it wobbles by 0.0636, which is numerical rather than statistical:")
    print("  25 training rows and degree 24 supplies exactly 25 features")

    rule("2. The same degree-24 model, with a penalty")
    reg = f.regularisation_sweep([0.0, 1e-6, 1e-3, 0.1, 1.0, 10.0, 100.0])
    print("      alpha    train MSE         test MSE")
    for alpha, train, test in reg:
        print(f"  {alpha:>9}   {train:10.4f}   {test:14.4f}")
    print(f"  lowest test error at alpha {f.best_alpha(reg)}")
    print(f"  the penalty improves the test error by a factor of "
          f"{reg[0][2] / min(r[2] for r in reg):.0f}")
    print("  training error rises with every increase in the penalty; that is the trade")

    rule("3. What more data fixes, and what it does not")
    data = f.data_sweep([15, 25, 50, 100, 400, 2000])
    print("      n    degree 1     degree 4        degree 24")
    for n, scores in data:
        print(f"  {n:5d}   {scores[1]:9.4f}   {scores[4]:9.4f}   {scores[24]:14.4f}")
    underfit = [scores[1] for _n, scores in data]
    overfit = [scores[24] for _n, scores in data]
    print(f"  underfit model, 15 rows to 2000 : {underfit[0]:.4f} -> {underfit[-1]:.4f}")
    print(f"  overfit model,  15 rows to 2000 : {overfit[0]:.4f} -> {overfit[-1]:.4f}")
    print(f"  the irreducible floor           : {f.irreducible_variance():.4f}")
    print("  more data cures overfitting completely and underfitting not at all")
    print(f"  the degree-24 column peaks at n=25, where features ({25}) equal rows")

    rule("4. The decomposition: bias squared, variance, noise")
    print("   deg     bias^2       variance      noise      predicted     observed")
    for degree, result in f.decomposition_table([1, 2, 3, 4, 6, 8, 12]):
        print(
            f"  {degree:4d}  {result['bias_squared']:10.4f}  {result['variance']:13.4f}  "
            f"{result['noise']:9.4f}  {result['predicted_total']:13.4f}  {result['observed']:13.4f}"
        )
    print("  underfitting is bias; overfitting is variance; the sum is the error")
    print("  degree 2 has MORE bias than degree 1 and twice the variance:")
    print("  the true function is odd, so a quadratic term buys nothing and costs")

    rule("5. Early stopping: the same model, trained for longer")
    train_history, test_history = f.training_history()
    best = int(np.argmin(test_history))
    print(f"  epochs run                        : {len(train_history)}")
    print(f"  training error falls every epoch  : {f.is_monotonically_decreasing(train_history)}")
    print(f"  training error, first to last     : {train_history[0]:.4f} -> {train_history[-1]:.4f}")
    print(f"  best test error                   : {test_history[best]:.4f} at epoch {best + 1}")
    print(f"  test error at epoch 600           : {test_history[-1]:.4f}")
    print(f"  worst test error after the best   : {max(test_history[best + 1:]):.4f}")
    print(f"  epochs worse than the best        : {sum(1 for v in test_history if v > min(test_history))} of 600")
    print(f"  generalisation gap, epoch 1       : {test_history[0] - train_history[0]:.4f}")
    print(f"  generalisation gap, epoch 600     : {test_history[-1] - train_history[-1]:.4f}")
    for patience in (5, 10, 20, 50):
        chosen = f.stop_with_patience(test_history, patience)
        print(f"  patience {patience:<3} would stop at epoch  : {chosen + 1} (test {test_history[chosen]:.4f})")
    print("  the test curve is not a clean U: it rises, then partly recovers,")
    print("  without ever again beating the value it reached at epoch 14")


if __name__ == "__main__":
    main()
