# Lab: Day 188 -- Recommender Systems

## Lesson
Day number: 188 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Recommender Systems and Matrix Factorization.

## Purpose
Build a complete, pure NumPy implementation of Matrix Factorization via Stochastic Gradient Descent (SGD / Funk SVD) from scratch. You will implement global baseline computation, user and item bias parameter learning, latent factor vector optimization with L2 regularization, and test rating prediction.

## Learning objectives
- Formulate sparse user-item interaction matrices.
- Compute global, user, and item baseline offsets.
- Implement SGD updates for user vectors p_u and item vectors q_i with L2 regularization.
- Evaluate prediction accuracy using Root Mean Squared Error (RMSE).

## Prerequisites
- Linear algebra: Vector dot products and matrix decomposition.
- Optimization: Gradient descent with L2 regularization penalty.
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
- `starter/recommender_systems_lib.py`: Student scaffold file.
- `examples/recommender_systems_lib.py`: Complete reference implementation.
- `tests/test_recommender_systems_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/recommender_systems_lib.py
```

## What the commands do
- Trains `MatrixFactorizationSGD` on a sparse rating dataset.
- Predicts missing star ratings for unobserved user-item pairs.
- Logs predicted rating values.

## Expected output
```
Recommender Demo: User 0 on Item 3 Predicted Rating = 4.12
```

## Validation steps
1. Check that learned global mean `mu` matches training dataset rating mean.
2. Verify that training RMSE converges smoothly below 0.5.
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
- **Exploding Loss:** Reduce learning rate `lr=0.01` and verify regularization lambda is positive.

## Security notes
All computations execute strictly on local CPU memory without network transmission.

## Extension exercises
1. Implement **Alternating Least Squares (ALS)** with parallel Ridge regression.
2. Implement **Bayesian Personalized Ranking (BPR)** for implicit feedback logs.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Recommender Systems
- **Day number:** 188 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-188-recommender-systems
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-188-recommender-systems` when the site is running.
<!-- generated-links:end -->
