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

import feedback_lib as f  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    X, y = f.iris_features_and_labels()

    print("Day 142 -- three kinds of feedback, measured")
    print("=" * 44)

    rule("1. Supervised: an answer per example")
    train, test = f.split_indices(len(y), 100, seed=142)
    print(f"  5-NN on iris, 100 train / 50 test      : {f.supervised_score(X, y, train, test):.4f}")

    rule("2. Unsupervised: the cluster numbers mean nothing")
    assignment = f.cluster(X, 3, seed=0).labels_
    raw = f.raw_cluster_accuracy(y, assignment)
    best, mapping = f.best_permutation_accuracy(y, assignment)
    print(f"  accuracy taking cluster ids literally  : {raw:.4f}")
    print(f"  accuracy after the best relabelling    : {best:.4f}  (mapping {mapping})")
    print(f"  difference, from numbering alone       : {best - raw:.4f}")

    rule("3. What k-means found on iris")
    table = f.cluster_confusion(y, assignment, 3, 3)
    print("  rows = species, columns = cluster id")
    for i, row in enumerate(table):
        print(f"    species {i}: {row.tolist()}")
    print("  species 0 is isolated exactly; species 1 and 2 share clusters")

    rule("4. Structure is not unique")
    scaled = f.cluster(f.standardise(X), 3, seed=0).labels_
    print(f"  ARI, raw clustering vs scaled          : {f.agreement(assignment, scaled):.4f}")
    print(f"  ARI, raw clustering vs true species    : {f.agreement(y, assignment):.4f}")
    print(f"  ARI, scaled clustering vs true species : {f.agreement(y, scaled):.4f}")
    print("  standardising moved AWAY from the species here")

    rule("5. k is a choice, not a discovery")
    ks = [2, 3, 4, 5, 6]
    inertia = f.inertia_curve(X, ks)
    silhouette = f.silhouette_curve(X, ks)
    for k, i, s in zip(ks, inertia, silhouette):
        print(f"    k={k}: inertia {i:8.3f}   silhouette {s:.4f}")
    print("  inertia falls at every step, so it can never choose k")
    print(f"  best silhouette is at k={ks[int(np.argmax(silhouette))]}; iris has 3 species")

    rule("6. Reinforcement: evaluative feedback (10 arms, 1000 steps, 200 runs)")
    rows = []
    for eps in (0.0, 0.01, 0.1):
        rows.append((eps,) + f.average_bandit(runs=200, k=10, steps=1000, epsilon=eps))
    for eps, reward, optimal in rows:
        print(f"    epsilon={eps:<5}: mean reward {reward:.4f}   optimal action {optimal:.4f}")
    print(f"  never exploring costs {rows[2][2] - rows[0][2]:.4f} of optimal-action rate")

    rule("7. Delayed feedback: a 5x5 gridworld, reward only at the goal")
    world = f.GridWorld(5)
    _q_bad, lengths_bad, reached_bad = f.q_learning(
        world, episodes=300, seed=0, break_ties_randomly=False
    )
    q_good, lengths_good, reached_good = f.q_learning(
        world, episodes=300, seed=0, break_ties_randomly=True
    )
    print(f"  shortest possible path                 : {world.shortest_path_length()} steps")
    print(f"  np.argmax tie-breaking, goal reached in : {reached_bad}/300 episodes")
    print(f"  random tie-breaking, goal reached in    : {reached_good}/300 episodes")
    print(f"  mean episode length, first 10           : {np.mean(lengths_good[:10]):.1f}")
    print(f"  mean episode length, last 10            : {np.mean(lengths_good[-10:]):.1f}")
    print(f"  greedy path after training              : {f.greedy_path_length(world, q_good)} steps")
    print("  how far the reward has travelled backwards:")
    for n, states, path in f.value_spread_by_episode(world, [1, 2, 3, 5, 10, 25, 50, 100, 300]):
        walk = "cannot reach goal" if path == 200 else f"{path} steps"
        print(f"    after {n:3d} episodes: {states:2d}/25 states valued, greedy policy {walk}")

    rule("8. A log is not a supervised dataset")
    arms, rewards, best_arm, counts = f.logged_policy_dataset(k=10, steps=2000, epsilon=0.1, seed=0)
    pulls = f.arm_pull_counts(counts)
    print(f"  seed 0, epsilon=0.1: best arm is {best_arm}, pulled {pulls[best_arm]} of 2000 times")
    print(f"  the other nine arms share {sum(v for a, v in pulls.items() if a != best_arm)} pulls")
    for eps, label in ((0.0, "greedy   "), (0.1, "epsilon=0.1")):
        verdicts = f.log_verdicts(range(8), epsilon=eps)
        right = sum(1 for row in verdicts if row[4])
        single = sum(1 for row in verdicts if row[1] == 1)
        print(f"  {label} logs: {right}/8 name the truly best arm; {single}/8 contain one arm only")
    arms1, rewards1, _b, counts1 = f.logged_policy_dataset(k=10, steps=2000, epsilon=0.1, seed=1)
    bandit1 = f.GaussianBandit(k=10, seed=1)
    means1 = f.logged_arm_means(arms1, rewards1)
    print("  the winner's curse, seed 1:")
    print(
        f"    arm 4: true {bandit1.means[4]:+.4f}  logged {means1[4]:+.4f}  "
        f"pulls {int(counts1[4])}"
    )
    print(
        f"    arm 1: true {bandit1.means[1]:+.4f}  logged {means1[1]:+.4f}  "
        f"pulls {int(counts1[1])}"
    )
    print(f"    the log picks arm {f.logged_best_arm(arms1, rewards1)}; the truth is arm 4")

    rule("9. Labels are the expensive part (iris, 1-NN, 40 repeats)")
    budgets = [3, 5, 10, 20, 50]
    curve = f.average_label_budget_curve(X, y, budgets, repeats=40)
    for b, score in zip(budgets, curve):
        print(f"    {b:2d} random labels : {score:.4f}")
    chosen = f.average_cluster_then_label(X, y, 3, repeats=40)
    ceiling = f.average_full_supervision(X, y, repeats=40)
    print(f"     3 chosen labels : {chosen:.4f}   (one per k-means cluster)")
    print(f"    100 labels       : {ceiling:.4f}   (every training row)")
    print(f"  three chosen labels beat three random ones by {chosen - curve[0]:.4f}")

    rule("10. Naming the setting before choosing an algorithm")
    cases = [
        ("labels, actions inert, feedback now  ", True, False, True),
        ("no labels, actions inert             ", False, False, True),
        ("labels, actions change the data, now ", True, True, True),
        ("labels, actions change the data, late", True, True, False),
    ]
    for label, has, acts, now in cases:
        verdict = f.classify_problem(
            f.problem(
                has_labels=has, actions_change_the_data=acts, feedback_is_immediate=now
            )
        )
        print(f"    {label} -> {verdict}")


if __name__ == "__main__":
    main()
