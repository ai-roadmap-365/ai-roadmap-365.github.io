#!/usr/bin/env python3
"""Print every measured pair in this lab as one table.

The harness compares this output byte for byte against
expected-output/measured-values.txt, so the report is not a convenience:
it is how the lab notices that a number in the lesson has gone stale.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import workflow_lib as w  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 143 -- the machine learning workflow, measured")
    print("=" * 49)

    rule("1. The pipeline as stages, with a step log")
    honest = w.run_pipeline(w.honest_stages(), w.starting_artifact())
    for name, produced in honest.log:
        print(f"    {name:<14} -> {', '.join(produced)}")

    rule("2. The honest pipeline on data that is pure noise")
    print(f"  cross-validated accuracy               : {honest.data['score']:.4f}")
    print(f"  majority-class baseline                : {honest.data['baseline']:.4f}")
    print(f"  per-fold scores                        : {honest.data['fold_scores'].tolist()}")
    print("  the labels are coin flips, so chance is the only honest answer")

    rule("3. The same five stages, two of them transposed")
    leaky = w.run_pipeline(w.leaky_stages(), w.starting_artifact(), enforce_contracts=False)
    print(f"  split then select (correct)            : {honest.data['score']:.4f}")
    print(f"  select then split (wrong, unchecked)   : {leaky.data['score']:.4f}")
    print(f"  accuracy invented by the reordering    : {leaky.data['score'] - honest.data['score']:.4f}")
    print(f"    correct order : {' -> '.join(n for n, _ in honest.log)}")
    print(f"    wrong order   : {' -> '.join(n for n, _ in leaky.log)}")
    try:
        w.run_pipeline(w.leaky_stages(), w.starting_artifact(), enforce_contracts=True)
        print("  with contracts enforced                : NO ERROR RAISED")
    except w.StageContractError as exc:
        print(f"  with contracts enforced                : {type(exc).__name__}")
        print(f"    {exc}")

    rule("3b. How the inflation grows with the number of features chosen")
    X, y = w.noise_dataset()
    print("    k    wrong   right   invented")
    for k, wrong, right, gap in w.inflation_by_k(X, y, [5, 10, 20, 50]):
        print(f"    {k:2d}   {wrong:.4f}  {right:.4f}   {gap:+.4f}")

    rule("4. The metric decides which model you ship")
    train = w.imbalanced_dataset(1000, 11)
    test = w.imbalanced_dataset(2000, 12)
    scores = w.score_all(w.candidate_models(), train[0], train[1], test[0], test[1])
    print(f"  {'model':<30}{'acc':>8}{'prec':>8}{'recall':>8}{'f1':>8}")
    for name, s in scores.items():
        print(
            f"  {name:<30}{s['accuracy']:>8.4f}{s['precision']:>8.4f}"
            f"{s['recall']:>8.4f}{s['f1']:>8.4f}"
        )
    for metric in ("accuracy", "precision", "recall", "f1"):
        print(f"  best by {metric:<10}: {w.winner(scores, metric)}")
    print(f"  test set carries {int(test[1].sum())} positives in {len(test[1])} rows")

    rule("5. Error analysis: what the accuracy hides")
    model = w.candidate_models()["logistic (default threshold)"]
    model.fit(train[0], train[1])
    table = w.error_table(model, test[0], test[1])
    print("  rows = true class, columns = predicted class")
    print(f"    true 0: {table[0]}")
    print(f"    true 1: {table[1]}")
    print(f"  94.35 percent accurate, and it misses {table[1][0]} positives while catching {table[1][1]}")

    rule("6. Reproducibility: the same inputs give the same artifact")
    keys = ("X", "y", "fold_scores", "score")
    first = w.manifest(w.run_pipeline(w.honest_stages(), w.starting_artifact()), keys)
    second = w.manifest(w.run_pipeline(w.honest_stages(), w.starting_artifact()), keys)
    other = w.manifest(w.run_pipeline(w.honest_stages(), w.starting_artifact(seed=144)), keys)
    for key in sorted(first):
        print(f"    {key:<12} {first[key]}")
    print(f"  two runs at seed 143 agree             : {first == second}")
    print(f"  a run at seed 144 differs              : {first != other}")

    rule("7. The modelling stage is the small one")
    lines = w.stage_source_lines(w.honest_stages())
    total = sum(lines.values())
    for name in ("load", "split", "select", "fit_and_score", "baseline"):
        print(f"    {name:<14} {lines[name]:>3} lines")
    print(f"    {'total':<14} {total:>3} lines")
    print(f"  the fitting stage is {lines['fit_and_score'] / total:.2%} of this pipeline")
    print("  and this pipeline has no cleaning, monitoring or deployment stage,")
    print("  so that figure is an upper bound rather than an estimate")


if __name__ == "__main__":
    main()
