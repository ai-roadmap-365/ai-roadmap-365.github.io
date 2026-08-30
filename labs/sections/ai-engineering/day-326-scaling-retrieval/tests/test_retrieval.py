"""Grouped by claim, so a failure names which property broke.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from retrieval import (  # noqa: E402
    BruteForceIndex,
    IVFIndex,
    cosine,
    make_vectors,
    recall_at_k,
    sweep_nprobe,
)

SMALL = 400
DIM = 16


def corpus(n: int = SMALL, seed: int = 7):
    return make_vectors(n, DIM, seed=seed, clusters=8)


# ----------------------------------------------------------------- geometry


def test_cosine_is_one_for_identical_vectors():
    v = [1.0, 2.0, 3.0]
    assert abs(cosine(v, v) - 1.0) < 1e-9


def test_cosine_handles_a_zero_vector_without_dividing_by_zero():
    assert cosine([0.0, 0.0], [1.0, 2.0]) == 0.0


def test_generated_vectors_are_clustered_not_uniform():
    # Approximate methods only help when the data has structure. If the
    # fixture were uniform noise, partitioning would buy nothing and the whole
    # lesson would be misleading.
    vectors = corpus()
    within = cosine(vectors[0], vectors[8])  # same cluster (n % 8)
    across = cosine(vectors[0], vectors[4])  # different cluster
    assert within > across


# -------------------------------------------------------------- exactness


def test_brute_force_returns_k_results_in_score_order():
    vectors = corpus()
    index = BruteForceIndex(vectors)
    query = vectors[0]
    got = index.search(query, 10)

    assert len(got) == 10
    assert got[0] == 0  # a vector is its own nearest neighbour
    scores = [cosine(query, vectors[i]) for i in got]
    assert scores == sorted(scores, reverse=True)


def test_brute_force_costs_one_comparison_per_vector():
    vectors = corpus()
    index = BruteForceIndex(vectors)
    index.search(vectors[0], 10)
    assert index.stats.comparisons == len(vectors)


# ------------------------------------------------------------- partitioning


def test_ivf_assigns_every_vector_to_exactly_one_list():
    vectors = corpus()
    index = IVFIndex(vectors, nlist=8)
    assigned = [i for lst in index.lists for i in lst]
    assert sorted(assigned) == list(range(len(vectors)))


def test_ivf_probing_every_list_matches_exact_search():
    # nprobe == nlist means no candidate is excluded, so recall must be
    # perfect. If this fails, the partitioning itself is losing vectors.
    vectors = corpus()
    exact = BruteForceIndex(vectors)
    index = IVFIndex(vectors, nlist=8)
    for q in (vectors[0], vectors[13], vectors[200]):
        assert recall_at_k(index.search(q, 10, nprobe=8), exact.search(q, 10)) == 1.0


def test_nprobe_is_clamped_to_the_valid_range():
    vectors = corpus()
    index = IVFIndex(vectors, nlist=8)
    assert len(index.search(vectors[0], 5, nprobe=0)) == 5
    assert len(index.search(vectors[0], 5, nprobe=99)) == 5


# ------------------------------------------------------------------ recall


def test_recall_counts_membership_not_order():
    assert recall_at_k([3, 2, 1], [1, 2, 3]) == 1.0
    assert recall_at_k([1, 2, 9], [1, 2, 3]) == 2 / 3
    assert recall_at_k([], [1, 2]) == 0.0


def test_recall_of_an_empty_truth_set_is_one():
    assert recall_at_k([1], []) == 1.0


# ------------------------------------------------------------- the tradeoff


def test_recall_rises_monotonically_with_nprobe():
    vectors = corpus()
    queries = corpus(20, seed=99)
    sweep = sweep_nprobe(vectors, queries, k=10, nlist=8)
    recalls = [row.recall for row in sweep.rows]
    assert recalls == sorted(recalls), f"recall should not fall as nprobe rises: {recalls}"


def test_cost_rises_monotonically_with_nprobe():
    vectors = corpus()
    queries = corpus(20, seed=99)
    sweep = sweep_nprobe(vectors, queries, k=10, nlist=8)
    costs = [row.comparisons for row in sweep.rows]
    assert costs == sorted(costs)


def test_full_probe_reaches_perfect_recall():
    vectors = corpus()
    queries = corpus(20, seed=99)
    sweep = sweep_nprobe(vectors, queries, k=10, nlist=8)
    assert sweep.rows[-1].recall == 1.0


def test_full_probe_costs_more_than_exact_search():
    # The honest part of the tradeoff: probing every list does all the work
    # brute force does, PLUS the centroid comparisons. An ANN index tuned for
    # perfect recall is strictly worse than not having one.
    vectors = corpus()
    queries = corpus(20, seed=99)
    sweep = sweep_nprobe(vectors, queries, k=10, nlist=8)
    assert sweep.rows[-1].comparisons > sweep.baseline_comparisons


def test_low_nprobe_is_much_cheaper_than_exact():
    vectors = corpus()
    queries = corpus(20, seed=99)
    sweep = sweep_nprobe(vectors, queries, k=10, nlist=8)
    assert sweep.rows[0].comparisons < sweep.baseline_comparisons / 3


def test_cheapest_meeting_returns_the_first_adequate_row():
    vectors = corpus()
    queries = corpus(20, seed=99)
    sweep = sweep_nprobe(vectors, queries, k=10, nlist=8)

    row = sweep.cheapest_meeting(0.80)
    assert row is not None and row.recall >= 0.80
    # It is the cheapest such row, so everything before it falls short.
    for earlier in sweep.rows[: row.nprobe - 1]:
        assert earlier.recall < 0.80


def test_an_unreachable_target_returns_none():
    vectors = corpus()
    queries = corpus(20, seed=99)
    sweep = sweep_nprobe(vectors, queries, k=10, nlist=8)
    assert sweep.cheapest_meeting(1.01) is None
