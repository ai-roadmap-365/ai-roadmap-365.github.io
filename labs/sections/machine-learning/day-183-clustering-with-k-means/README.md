# Lab: Day 183 -- Clustering with k-means

## Lesson
Day number: 183 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: K-Means Clustering, Lloyd's Coordinate Descent, and k-means++ Seeding.

## Purpose
Build a complete, pure NumPy implementation of the K-Means clustering algorithm from scratch. You will implement k-means++ distance-squared probability initialization, the alternating expectation assignment step, the maximization centroid recalculation step, and compute the final WCSS inertia.

## Learning objectives
- Implement k-means++ distance-squared probability seeding.
- Implement Lloyd's alternating expectation-maximization coordinate descent.
- Calculate Within-Cluster Sum of Squares (WCSS / Inertia).
- Assign unseen test points to their nearest cluster centroid in Euclidean metric space.

## Prerequisites
- Linear algebra: Matrix operations, Euclidean norm calculations.
- Probability: Discrete probability sampling with `np.random.choice`.
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
- `starter/clustering_with_k_means_lib.py`: Student scaffold file.
- `examples/clustering_with_k_means_lib.py`: Complete reference implementation.
- `tests/test_clustering_with_k_means_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/clustering_with_k_means_lib.py
```

## What the commands do
- Initializes 3 Gaussian blobs with 300 total points in 2D space.
- Runs `KMeansFromScratch` with `k-means++` initialization until centroid convergence.
- Prints the final converged WCSS Inertia.

## Expected output
```
K-Means converged with Inertia: 354.93
```

## Validation steps
1. Check that `_init_centroids` selects well-dispersed points using D^2 probability.
2. Verify that `fit()` iterates until centroid movement is less than `tol`.
3. Verify that `predict()` returns integer cluster IDs `[0, K-1]`.
4. Ensure all test cases pass.

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
- **Empty Cluster Error:** If a cluster has 0 assigned points during update, reassign its centroid to a randomly chosen sample point.
- **Slow Convergence:** Ensure tolerance `tol=1e-4` is checked against the Euclidean norm of centroid shifts.

## Security notes
All computations run strictly on local CPU memory. No telemetry or network connections are initiated.

## Extension exercises
1. Implement **Mini-Batch K-Means** using random sub-samples of size 64.
2. Implement **Silhouette Score calculation** in pure NumPy.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Clustering with k-means
- **Day number:** 183 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-183-clustering-with-k-means
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-183-clustering-with-k-means` when the site is running.
<!-- generated-links:end -->
