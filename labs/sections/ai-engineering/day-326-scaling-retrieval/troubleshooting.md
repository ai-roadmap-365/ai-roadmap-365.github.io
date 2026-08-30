# Troubleshooting — Day 326

## Recall at `nprobe=8` is below 1.0

Probing every list means excluding no candidate, so recall must be exactly 1.0. If it is not, the partitioning itself is losing vectors — usually because `_build` leaves some vectors unassigned, or because a list is dropped when it comes out empty.

Check with:

```bash
python3 -c "
import sys; sys.path.insert(0,'examples')
from retrieval import make_vectors, IVFIndex
v = make_vectors(400, 16, seed=7)
idx = IVFIndex(v, nlist=8)
assigned = sorted(i for lst in idx.lists for i in lst)
print('assigned', len(assigned), 'of', len(v), '| duplicates:', len(assigned)!=len(set(assigned)))"
```

## Recall falls as `nprobe` rises

You are selecting the *furthest* centroids rather than the nearest. Cosine similarity is higher for closer vectors, so the sort must be descending on similarity — `key=lambda c: -cosine(...)`, or `reverse=True`.

## Full probe costs the same as exact search rather than more

You are not counting the centroid comparisons. They are real work done on every query regardless of `nprobe`, and they are exactly why full probing is worse than brute force. Add `self.stats.comparisons += self.nlist` before ranking the centroids.

## Every recall is 1.0 at every `nprobe`

Your corpus is too small, or the clusters are so tight that the nearest list always contains all the true neighbours. Increase the corpus size or `nlist`, or widen the Gaussian spread in `make_vectors`.

## The numbers do not match the documented table

The generator is seeded, so a correct implementation reproduces it exactly. Differences usually come from one of three places: a different tie-breaking rule in the sort (break ties by index), a different number of k-means rounds in `_build`, or counting comparisons at a different point.

## `ZeroDivisionError` in `cosine`

A zero vector has no direction, so cosine is undefined. Return `0.0` rather than raising — `test_cosine_handles_a_zero_vector_without_dividing_by_zero` checks this.

## `recall_at_k` fails on the empty case

An empty truth set means there was nothing to find, so recall is 1.0 by convention rather than a division by zero.

## The suite is slow

Two seconds is expected: the sweep builds a fresh IVF index for every `nprobe` setting, and k-means runs six rounds each time. If it is much slower, check that `_build` is not being called inside the per-query loop.

## `NotImplementedError` everywhere

Expected. The starter stubs `cosine`, `recall_at_k`, `BruteForceIndex.search` and `IVFIndex.search` — see `expected-output/starter-run.txt`.
