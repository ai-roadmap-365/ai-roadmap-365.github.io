"""Exact versus approximate retrieval, and the recall you trade for speed.

Offline, standard-library only, and deterministic: every vector comes from a
seeded generator, so the numbers in the lesson are reproducible rather than
"about right".

Cost is measured in **vector comparisons**, not wall-clock seconds. That is a
deliberate choice. Wall-clock on a laptop is dominated by interpreter overhead
and whatever else the machine is doing, so it makes a poor teaching signal and
a worse test assertion. Comparisons are the thing an ANN index actually
reduces, they are exactly reproducible, and they scale the same way the real
cost does. The lesson says where this abstraction stops being true.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


@dataclass
class Stats:
    """How much work a search did."""

    comparisons: int = 0

    def reset(self) -> None:
        self.comparisons = 0


def make_vectors(n: int, dim: int, *, seed: int = 7, clusters: int = 8) -> list[list[float]]:
    """Generate clustered vectors, because real embeddings are not uniform.

    Uniform random points would make every approximate method look terrible:
    partitioning only helps when the data has structure to partition. Real
    corpora cluster by topic, so the fixture does too.
    """
    rng = random.Random(seed)
    centres = [[rng.uniform(-1, 1) for _ in range(dim)] for _ in range(clusters)]
    out: list[list[float]] = []
    for i in range(n):
        centre = centres[i % clusters]
        out.append([c + rng.gauss(0, 0.15) for c in centre])
    return out


def cosine(a: list[float], b: list[float]) -> float:
    # TASK 1: cosine similarity. Return 0.0 if either vector has zero norm
    # rather than dividing by zero.
    raise NotImplementedError("implement cosine")

class BruteForceIndex:
    """Exact search. Always correct, and always O(n) per query."""

    def __init__(self, vectors: list[list[float]]) -> None:
        self.vectors = vectors
        self.stats = Stats()

    def search(self, query: list[float], k: int) -> list[int]:
        # TASK 3: exact search. Count one comparison per vector, score every
        # one with cosine, and return the k best indices. Break ties by
        # index so the ordering is deterministic.
        raise NotImplementedError("implement BruteForceIndex.search")


class IVFIndex:
    """Inverted-file index: partition into lists, search only the nearest few.

    This is the shape of a real IVF index. Build assigns each vector to its
    nearest centroid; search compares the query to every centroid, picks the
    `nprobe` closest lists, and scans only those. The recall loss comes from
    one specific place: a true neighbour sitting in a list you did not probe.
    """

    def __init__(self, vectors: list[list[float]], *, nlist: int = 8, seed: int = 11) -> None:
        self.vectors = vectors
        self.nlist = nlist
        self.stats = Stats()
        self.centroids, self.lists = self._build(seed)

    def _build(self, seed: int) -> tuple[list[list[float]], list[list[int]]]:
        """Assign vectors to lists with a few rounds of Lloyd's algorithm."""
        rng = random.Random(seed)
        dim = len(self.vectors[0])
        centroids = [list(self.vectors[rng.randrange(len(self.vectors))]) for _ in range(self.nlist)]

        lists: list[list[int]] = [[] for _ in range(self.nlist)]
        for _ in range(6):
            lists = [[] for _ in range(self.nlist)]
            for i, v in enumerate(self.vectors):
                best = max(range(self.nlist), key=lambda c: cosine(v, centroids[c]))
                lists[best].append(i)
            for c in range(self.nlist):
                if not lists[c]:
                    continue
                centroids[c] = [
                    sum(self.vectors[i][d] for i in lists[c]) / len(lists[c]) for d in range(dim)
                ]
        return centroids, lists

    def search(self, query: list[float], k: int, *, nprobe: int = 1) -> list[int]:
        # TASK 4: probe search.
        #   - clamp nprobe into [1, self.nlist]
        #   - count self.nlist centroid comparisons; they are real work, and
        #     they are exactly why full probing costs MORE than exact search
        #   - take the nprobe NEAREST centroids (watch the sort direction)
        #   - gather those lists' vectors, count one comparison each, and
        #     return the k best
        raise NotImplementedError("implement IVFIndex.search")


def recall_at_k(approximate: list[int], exact: list[int]) -> float:
    """Fraction of the true top-k that the approximate search also returned.

    Note what this does NOT measure: ordering. An index that returns all the
    right documents in the wrong order scores 1.0 here, which is usually the
    right call for retrieval feeding a reranker, and the wrong one if the raw
    order is shown to a user.
    """
    # TASK 2: fraction of `exact` that also appears in `approximate`.
    # Membership, not order: [3,2,1] against [1,2,3] is 1.0.
    # An empty truth set is 1.0, not a division by zero.
    raise NotImplementedError("implement recall_at_k")

@dataclass
class SweepRow:
    nprobe: int
    recall: float
    comparisons: int

    def line(self, baseline: int) -> str:
        speedup = baseline / self.comparisons if self.comparisons else 0.0
        return (
            f"nprobe={self.nprobe:<2} recall@10={self.recall:.2f} "
            f"comparisons={self.comparisons:<6} speedup={speedup:.1f}x"
        )


@dataclass
class Sweep:
    rows: list[SweepRow] = field(default_factory=list)
    baseline_comparisons: int = 0

    def cheapest_meeting(self, target: float) -> SweepRow | None:
        """The least work that still reaches a recall target.

        This is the question worth asking of an ANN index -- not "what is the
        best recall" but "what is the cheapest configuration good enough for
        the job".
        """
        for row in self.rows:
            if row.recall >= target:
                return row
        return None


def sweep_nprobe(
    vectors: list[list[float]],
    queries: list[list[float]],
    *,
    k: int = 10,
    nlist: int = 8,
) -> Sweep:
    """Measure recall and cost across every nprobe setting."""
    exact = BruteForceIndex(vectors)
    truth = [exact.search(q, k) for q in queries]
    baseline = exact.stats.comparisons

    result = Sweep(baseline_comparisons=baseline)
    for nprobe in range(1, nlist + 1):
        index = IVFIndex(vectors, nlist=nlist)
        recalls = []
        for query, want in zip(queries, truth):
            got = index.search(query, k, nprobe=nprobe)
            recalls.append(recall_at_k(got, want))
        result.rows.append(
            SweepRow(
                nprobe=nprobe,
                recall=sum(recalls) / len(recalls),
                comparisons=index.stats.comparisons,
            )
        )
    return result
