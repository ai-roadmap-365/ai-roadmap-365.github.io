# Lab — Day 325: Keeping Indexes Fresh

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Keeping Indexes Fresh
- **Day number:** 325 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-325-keeping-indexes-fresh
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-325-keeping-indexes-fresh` when the site is running.
<!-- generated-links:end -->

## Purpose

Build a freshness checker that measures how far an index has drifted from its source, rather than assuming it has not. You classify every document into one of four drift categories, measure staleness as a distribution, guard deletion against a failed source enumeration, and reconcile until the two sides agree.

Everything runs offline against in-memory state, using a logical clock so the results are deterministic.

## Learning objectives

- Classify drift into fresh, missing, stale and orphaned, and explain why they differ in consequence.
- Compare over the union of both id sets, and explain why a source-driven scan cannot find an orphan.
- Report staleness as a percentile over per-document ages rather than a count.
- Refuse a reconciliation that would delete an implausible share of the index.
- Show that a correct reconciliation converges on a second run.

## Prerequisites

- Day 323, "Data Ingestion Pipelines" — the content hash used as a version here comes from there.
- Day 324, "Document Processing at Scale".
- Comfortable with Python dictionaries, sets and enums.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no hosted service. The lesson discusses Elasticsearch aliases, Debezium and Dagster freshness policies as real-world options; none is required here.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/freshness.py         your work: compare, staleness_age, percentile,
                             reconcile, safe_to_delete
examples/freshness.py        reference implementation
examples/freshness_demo.py   compares a drifted pair and reconciles it
tests/test_freshness.py      grouped by concern
tests/run_tests.sh           suite entry point
expected-output/             real captured output and measured values
requirements/                pinned dependency
```

## How to run

```bash
python3 examples/freshness_demo.py   # classify, measure, guard, reconcile
bash tests/run_tests.sh              # run the suite
```

To work on the exercise, edit `starter/freshness.py`, then copy it over the reference:

```bash
cp starter/freshness.py examples/freshness.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/freshness_demo.py` builds a source and an index that disagree in every possible way, prints one line per document, reports staleness ages and a p95, checks the delete guard, reconciles, and compares again to show convergence.

`bash tests/run_tests.sh` runs `pytest` over seventeen tests grouped by concern — classification, staleness, reconciliation and the delete guard.

## Expected output

```text
doc-1    stale     index at v1, source at v2
doc-2    fresh
doc-3    stale     index at v4, source at v5
doc-4    missing   at source, not indexed
doc-9    orphaned  deleted at source, still indexed
fresh=1 missing=1 stale=2 orphaned=1
staleness ages: {'doc-1': 10, 'doc-3': 2}
p95 staleness: 10 ticks
safe to delete: True
indexed=1 updated=2 deleted=1
after reconcile: fresh=4 missing=0 stale=0 orphaned=0
```

`doc-9` is the document to notice: it is not at the source at all, so any process starting from "for each document in the source" walks straight past it. `expected-output/FIELDS.md` explains each part.

## Validation steps

1. `bash tests/run_tests.sh` reports `17 passed`.
2. Reconcile twice. The second run must report `indexed=0 updated=0 deleted=0` — a correct reconciliation converges.
3. Build a state with an empty source and twenty indexed documents. `safe_to_delete` must return `False`; that shape is a broken enumeration, not a mass deletion.

## Tests

Seventeen tests in four groups:

- **classification** — each category is identified; every document lands in exactly one; the comparison walks the union rather than the source.
- **staleness** — ages cover only stale documents, are never negative, and the percentile uses nearest rank (`ceil`, not `round`).
- **reconcile** — every category is fixed, the result is idempotent, and deletes can be withheld.
- **delete guard** — an implausible mass deletion is blocked, a normal one is allowed, an empty index is safe, and the threshold is configurable.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md` for each failure this lab is designed to produce.

## Security notes

See `security.md`. In short: no network, no credentials, no API key. The delete guard is itself a security control, and deletion propagation is where right-to-erasure is actually honoured.

## Extension exercises

1. **Per-partition reconciliation.** Reconcile one partition per run, track when each was last checked, and apply the delete guard per partition rather than globally.
2. **A freshness objective.** State a target such as p95 staleness under ten ticks with zero orphans, and report an error budget against it over a simulated week of intermittent failures. Report honestly whether it was met.
3. **Adaptive scheduling.** Track how often each document changes and check volatile documents more frequently, then measure whether p95 staleness actually improved for the same number of checks.

## Navigation

- [Lesson](../../../../content/sections/ai-engineering/day-325-keeping-indexes-fresh/README.md)
- Previous: Day 324 — Document Processing at Scale
- Next: Day 326 — Scaling Retrieval
