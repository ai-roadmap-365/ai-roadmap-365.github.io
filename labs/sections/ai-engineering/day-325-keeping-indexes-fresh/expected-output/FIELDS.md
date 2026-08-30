# Reading the freshness output

## The per-document lines

    doc-1    stale     index at v1, source at v2

| Part | Meaning |
| --- | --- |
| id | The document. |
| drift | One of `fresh`, `missing`, `stale`, `orphaned` — every document lands in exactly one. |
| detail | For `stale`, both versions. For `missing` and `orphaned`, which side has it. `fresh` has none. |

## The summary line

    fresh=1 missing=1 stale=2 orphaned=1

Counts per category. `orphaned` is the one to watch: it is the only category a source-driven scan cannot produce, and the only one that can mean deleted content is still being quoted.

## Staleness

    staleness ages: {'doc-1': 10, 'doc-3': 2}
    p95 staleness: 10 ticks

Ages, not counts. Both documents are stale, but `doc-1` has been stale five times longer — the count treats them identically and the ages do not. Ticks are a logical clock so the tests are deterministic; in production this is wall-clock time.

## The guard and the reconcile

    safe to delete: True
    indexed=1 updated=2 deleted=1
    after reconcile: fresh=4 missing=0 stale=0 orphaned=0

One orphan out of four indexed documents is 25 percent, exactly at the default threshold, so deletion is permitted. Had the source enumeration returned nothing, all four would have looked orphaned, the fraction would have been 100 percent, and the guard would have refused the run outright.

The final line is the convergence check: everything fresh, nothing left in any other category.
