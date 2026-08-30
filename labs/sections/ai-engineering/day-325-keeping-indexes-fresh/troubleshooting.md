# Troubleshooting — Day 325

## No orphans are ever found

You are iterating `source` rather than `set(source) | set(index)`. An orphan is by definition a document the source no longer mentions, so a source-driven loop can never visit it. This is the most common bug in this area and the reason deletions silently fail to propagate in real systems.

Check with:

```bash
python3 -c "
import sys; sys.path.insert(0,'examples')
from freshness import compare, Record, Drift
r = compare({}, {'gone': Record('gone','v1',0)})
print(r.count(Drift.ORPHANED))   # must be 1"
```

## The p50 of `[1, 2, 3, 4, 100]` comes out as 2

You used `round` for the nearest-rank calculation. Python rounds halves to even, so `round(2.5)` is 2 and you land on the wrong observation. Nearest rank is `math.ceil(p / 100 * N)`.

## `test_staleness_age_is_never_negative` fails

A source document can carry an `updated_at` later than `now` — a clock skew, or a test constructing it deliberately. Floor the result at zero rather than returning a negative age.

## Reconciliation is not idempotent

Either you are mutating the index while iterating a report built from the pre-reconcile state in a way that skips entries, or your version comparison is not symmetric with what you write. Recompute the report after reconciling and assert every document is fresh.

## The guard blocks a run you expected to succeed

The threshold is a fraction of the **indexed** total — fresh plus stale plus orphaned — not of the source total. An index holding four documents with one orphan is at exactly 25 percent, which the default permits. Five documents with two orphans is 40 percent, which it does not.

## `ZeroDivisionError` in `safe_to_delete`

An empty index is a normal state, especially on a first run. Return `True` when the indexed total is zero rather than dividing.

## `KeyError` during reconcile

You are deleting from `index` while iterating over it, or looking up a `MISSING` document in `index` rather than in `source`. Iterate `report.findings`, which is a snapshot, and take the record from the side that actually has it.

## `NotImplementedError` everywhere

Expected. The starter stubs all five functions, and every test depends on at least one — see `expected-output/starter-run.txt`.
