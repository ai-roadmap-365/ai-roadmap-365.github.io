# Lab: Day 189 -- A Segmentation Study

## Lesson
Day number: 189 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Comprehensive Customer Segmentation and Persona Profiling Study.

## Purpose
Build a complete, end-to-end customer segmentation pipeline from scratch in pure NumPy. You will implement non-linear log-standardization for power-law financial features, PCA variance-preserving dimensionality reduction, K-Means++ centroid clustering, and unscaled persona profile synthesis.

## Learning objectives
- Process raw transactional RFM metrics with logarithmic scaling.
- Apply PCA to eliminate collinearity and extract orthogonal feature axes.
- Implement K-Means++ clustering with probabilistic seeding.
- Profile and denormalize cluster centroids into actionable marketing personas.

## Prerequisites
- Days 183-188: K-Means, PCA, SVD, and unsupervised validation metrics.
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
- `starter/a_segmentation_study_lib.py`: Student scaffold file.
- `examples/a_segmentation_study_lib.py`: Complete reference implementation.
- `tests/test_a_segmentation_study_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/a_segmentation_study_lib.py
```

## What the commands do
- Generates a synthetic dataset of 400 customer records spanning 4 behavioral archetypes.
- Executes `CustomerSegmentationPipeline` to log-transform, PCA compress, and cluster records.
- Computes unscaled persona profile statistics.

## Expected output
```
Segmentation Demo: Processed 400 customers into 4 personas.
```

## Validation steps
1. Check that discovered clusters contain non-zero sample counts.
2. Verify that persona profile metrics reflect original unscaled dollar and day units.
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
- **Zero Variance Features:** Add epsilon `1e-12` to standard deviation denominators during scaling.

## Security notes
All computations execute strictly on local CPU memory without external network transmission.

## Extension exercises
1. Implement **Gaussian Mixture Model (GMM)** soft clustering for hybrid persona assignments.
2. Build an automated **Elbow Plot Sweeper** in matplotlib.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Segmentation Study
- **Day number:** 189 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-189-a-segmentation-study
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-189-a-segmentation-study` when the site is running.
<!-- generated-links:end -->
