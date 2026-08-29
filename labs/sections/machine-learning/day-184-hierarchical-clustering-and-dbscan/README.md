# Lab: Day 184 -- Hierarchical Clustering and DBSCAN

## Lesson
Day number: 184 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Hierarchical Clustering and DBSCAN.

## Purpose
Build a complete, pure NumPy implementation of the DBSCAN density clustering algorithm from scratch. You will implement epsilon-neighborhood range queries, core point identification, breadth-first density cluster expansion, and noise classification.

## Learning objectives
- Implement epsilon-radius Euclidean neighborhood queries.
- Identify core, border, and noise observations.
- Expand density clusters using iterative queue traversal.
- Benchmark clustering performance on non-spherical datasets with noise.

## Prerequisites
- Linear algebra: Pairwise Euclidean distance matrices.
- Data structures: Queue-based breadth-first traversal.
- Python 3.11+ with NumPy.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 512 MB RAM.
- 50 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
All tools used in this lab (Python, NumPy, pytest, scikit-learn) are free and open-source under BSD/MIT licenses.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/hierarchical_clustering_and_dbscan_lib.py`: Student scaffold file.
- `examples/hierarchical_clustering_and_dbscan_lib.py`: Complete reference implementation.
- `tests/test_hierarchical_clustering_and_dbscan_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/hierarchical_clustering_and_dbscan_lib.py
```

## What the commands do
- Generates two Gaussian clusters with 100 points plus 3 isolated outlier noise points.
- Runs `DBSCANFromScratch` with epsilon=0.8 and MinPts=5.
- Logs the number of discovered clusters and verified noise points.

## Expected output
```
DBSCAN Demo: Discovered 2 clusters with 3 noise points.
```

## Validation steps
1. Verify that all points in core neighborhoods are assigned to matching cluster IDs.
2. Verify that isolated outliers receive label `-1`.
3. Ensure all unit test assertions pass.

## Tests
Run the test runner script:
```bash
./tests/run_tests.sh
```

## Cleanup
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
```

## Troubleshooting
- **All Points Noise:** Epsilon radius is too small. Check scale of features.
- **Single Giant Cluster:** Epsilon radius is too large, causing clusters to merge across noise.

## Security notes
All computations run strictly on local CPU memory without network transmission.

## Extension exercises
1. Implement **KD-Tree spatial indexing** to optimize neighborhood range queries from O(N^2) to O(N log N).
2. Implement **Ward hierarchical clustering** dendrogram tree building.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Hierarchical Clustering and DBSCAN
- **Day number:** 184 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-184-hierarchical-clustering-and-dbscan
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-184-hierarchical-clustering-and-dbscan` when the site is running.
<!-- generated-links:end -->
