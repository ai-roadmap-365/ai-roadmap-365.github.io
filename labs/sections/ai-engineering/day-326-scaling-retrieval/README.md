# Lab — Day 326: Scaling Retrieval

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Scaling Retrieval
- **Day number:** 326 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-326-scaling-retrieval
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-326-scaling-retrieval` when the site is running.
<!-- generated-links:end -->

## Purpose

Measure the recall you trade for speed, rather than accepting a library's default. You implement exact search and an inverted-file index side by side, sweep the tuning parameter, and produce the recall-versus-cost curve for a corpus you control.

Everything is deterministic: the vectors come from a seeded generator, so the numbers reproduce exactly.

## Learning objectives

- Implement exact nearest-neighbour search and count its cost honestly.
- Build an IVF index and identify precisely where its recall loss originates.
- Measure recall at k against an exact baseline.
- Sweep `nprobe` and locate the knee of the curve.
- Demonstrate that full probing costs more than exact search, and explain why.

## Prerequisites

- Day 325, "Keeping Indexes Fresh" — an ANN index is a derived structure with exactly those freshness problems.
- Comfortable with Python lists, sorting with keys, and basic vector arithmetic.
- No linear-algebra library needed; cosine similarity is written by hand.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in about 2.3 seconds and uses a few megabytes.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no hosted service. The lesson discusses FAISS, hnswlib, pgvector, Qdrant and Milvus as the real-world open-source options; none is required here, and the algorithms are written out so nothing is hidden behind a library default.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/retrieval.py         your work: cosine, recall_at_k, both searches
examples/retrieval.py        reference implementation
examples/retrieval_demo.py   sweeps nprobe and prints the curve
tests/test_retrieval.py      grouped by claim
tests/run_tests.sh           suite entry point
expected-output/             real captured output and measured values
requirements/                pinned dependency
```

## How to run

```bash
python3 examples/retrieval_demo.py   # sweep nprobe, print the curve
bash tests/run_tests.sh              # run the suite
```

To work on the exercise, edit `starter/retrieval.py`, then copy it over the reference:

```bash
cp starter/retrieval.py examples/retrieval.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/retrieval_demo.py` builds 2,000 clustered vectors, runs exact search to establish ground truth, then runs IVF at every `nprobe` from 1 to 8, reporting mean recall and total comparisons for each — followed by the cheapest setting that reaches each of three recall targets.

`bash tests/run_tests.sh` runs `pytest` over seventeen tests grouped by claim: geometry, exactness, partitioning, recall and the trade-off itself.

## Expected output

```text
corpus=2000 dim=32 queries=20 k=10 nlist=8
exact search cost: 40000 comparisons
nprobe=1  recall@10=0.81 comparisons=6192   speedup=6.5x
nprobe=2  recall@10=0.88 comparisons=12051  speedup=3.3x
nprobe=3  recall@10=0.90 comparisons=16325  speedup=2.5x
nprobe=4  recall@10=0.97 comparisons=20474  speedup=2.0x
nprobe=5  recall@10=0.97 comparisons=23575  speedup=1.7x
nprobe=6  recall@10=0.97 comparisons=27527  speedup=1.5x
nprobe=7  recall@10=0.98 comparisons=34559  speedup=1.2x
nprobe=8  recall@10=1.00 comparisons=40160  speedup=1.0x
recall>=0.90: nprobe=3 (2.5x cheaper than exact)
recall>=0.95: nprobe=4 (2.0x cheaper than exact)
recall>=0.99: nprobe=8 (1.0x cheaper than exact)
```

Note the last data row: `nprobe=8` costs 40,160 comparisons where exact search costs 40,000. `expected-output/FIELDS.md` explains every field and why the cost metric is comparisons rather than seconds.

## Validation steps

1. `bash tests/run_tests.sh` reports `17 passed`.
2. Your demo output must match the table above exactly — the generator is seeded. A mismatch means your clustering or your comparison counting differs.
3. Confirm recall never falls as `nprobe` rises, and that `nprobe=8` gives exactly `1.00`. Anything less means your partitioning is losing vectors.

## Tests

Seventeen tests in five groups:

- **geometry** — cosine is 1.0 for identical vectors, handles a zero vector, and the fixture is genuinely clustered rather than uniform.
- **exactness** — brute force returns k results in score order and costs one comparison per vector.
- **partitioning** — every vector is in exactly one list, full probe matches exact search, and `nprobe` is clamped.
- **recall** — membership not ordering; an empty truth set is 1.0.
- **the trade-off** — recall and cost both rise monotonically, full probe reaches 1.0 and costs more than exact, low probe is far cheaper, and the target search returns the cheapest adequate row.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md` for each failure this lab is designed to produce.

## Security notes

See `security.md`. In short: no network, no credentials, no API key. The lesson covers the multi-tenant leakage and right-to-erasure issues that real ANN indexes raise.

## Extension exercises

1. **Per-query recall.** Report the minimum and the count of queries below 0.5, then find a setting where the mean looks fine but a query returns nothing.
2. **Scalar quantisation.** Store components as 8-bit integers, measure the memory saved and the recall lost, and find the corpus size at which quantised IVF beats exact search on both. "Never, at this size" is a legitimate finding.
3. **Compare to a graph index.** Implement a simple navigable small-world graph and put its curve alongside IVF's on the same corpus.

## Navigation

- [Lesson](../../../../content/sections/ai-engineering/day-326-scaling-retrieval/README.md)
- Previous: Day 325 — Keeping Indexes Fresh
- Next: Day 327 — Cost Engineering for AI Systems
