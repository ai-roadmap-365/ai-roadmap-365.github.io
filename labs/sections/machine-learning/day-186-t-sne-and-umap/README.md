# Lab: Day 186 -- t-SNE and UMAP

## Lesson
Day number: 186 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: t-SNE, UMAP, and Non-Linear Manifold Dimensionality Reduction.

## Purpose
Build a complete, pure NumPy implementation of t-Distributed Stochastic Neighbor Embedding (t-SNE) from scratch. You will implement high-dimensional Gaussian affinity matrix construction, low-dimensional Student-t probability calculation, analytical KL-divergence gradient computation, and momentum-based coordinate updates.

## Learning objectives
- Calculate pairwise Gaussian probability affinities with adaptive variance.
- Symmetrize probability distributions and apply early exaggeration.
- Compute low-dimensional Student-t probabilities to prevent crowding.
- Execute gradient descent with momentum on coordinate embeddings.

## Prerequisites
- Multivariable calculus: Gradient descent optimization.
- Probability: Gaussian and Student-t probability density distributions, KL divergence.
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
- `starter/t_sne_and_umap_lib.py`: Student scaffold file.
- `examples/t_sne_and_umap_lib.py`: Complete reference implementation.
- `tests/test_t_sne_and_umap_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/t_sne_and_umap_lib.py
```

## What the commands do
- Generates two 4D Gaussian clusters with 80 total samples.
- Executes `TSNEFromScratch` to optimize 2D embedding coordinates.
- Logs output embedding dimensions.

## Expected output
```
t-SNE Demo: Transformed (80, 4) to Embedding (80, 2)
```

## Validation steps
1. Verify that high-dimensional affinity matrix P is symmetric and sums to 1.0.
2. Verify that low-dimensional embedding coordinates Y do not contain `NaN`.
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
- **Exploding Gradients:** Reduce learning rate `lr=50.0` or increase coordinate epsilon floor.

## Security notes
All computations run strictly on local CPU memory without network transmission.

## Extension exercises
1. Implement **Barnes-Hut quad-tree spatial acceleration**.
2. Benchmark t-SNE against UMAP on the MNIST handwriting dataset.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** t-SNE and UMAP
- **Day number:** 186 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-186-t-sne-and-umap
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-186-t-sne-and-umap` when the site is running.
<!-- generated-links:end -->
