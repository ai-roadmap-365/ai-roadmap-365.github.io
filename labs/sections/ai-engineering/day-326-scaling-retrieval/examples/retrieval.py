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
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


class BruteForceIndex:
    """Exact search. Always correct, and always O(n) per query."""

    def __init__(self, vectors: list[list[float]]) -> None:
        self.vectors = vectors
        self.stats = Stats()

    def search(self, query: list[float], k: int) -> list[int]:
        self.stats.comparisons += len(self.vectors)
        scored = [(cosine(query, v), i) for i, v in enumerate(self.vectors)]
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        return [i for _, i in scored[:k]]


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
        nprobe = max(1, min(nprobe, self.nlist))

        # Comparing against the centroids is real work and is counted.
        self.stats.comparisons += self.nlist
        ranked = sorted(
            range(self.nlist), key=lambda c: (-cosine(query, self.centroids[c]), c)
        )[:nprobe]

        candidates: list[int] = []
        for c in ranked:
            candidates.extend(self.lists[c])

        self.stats.comparisons += len(candidates)
        scored = [(cosine(query, self.vectors[i]), i) for i in candidates]
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        return [i for _, i in scored[:k]]


def recall_at_k(approximate: list[int], exact: list[int]) -> float:
    """Fraction of the true top-k that the approximate search also returned.

    Note what this does NOT measure: ordering. An index that returns all the
    right documents in the wrong order scores 1.0 here, which is usually the
    right call for retrieval feeding a reranker, and the wrong one if the raw
    order is shown to a user.
    """
    if not exact:
        return 1.0
    return len(set(approximate) & set(exact)) / len(exact)


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
