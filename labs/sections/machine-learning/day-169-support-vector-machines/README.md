# Lab 169: Support Vector Machines and Kernel Methods from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Support Vector Machines
- **Day number:** 169 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-169-support-vector-machines
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-169-support-vector-machines` when the site is running.
<!-- generated-links:end -->

## Purpose
Build Support Vector Machine algorithms from first principles: implement pairwise RBF Gaussian kernel Gram matrix generation, code the Pegasos subgradient descent optimizer on Hinge Loss, and benchmark against scikit-learn's `SVC` and `LinearSVC`.

## Learning objectives
1. Formulate the soft-margin geometric margin optimization problem.
2. Implement vectorized pairwise RBF (Gaussian) kernel Gram matrix computation.
3. Code the Pegasos subgradient descent algorithm for linear SVMs with Hinge Loss.
4. Explain the role of support vectors and the Karush-Kuhn-Tucker (KKT) conditions.
5. Benchmark linear vs kernel SVMs and evaluate why feature scaling is strictly mandatory.

## Prerequisites
- Linear regression and loss functions (Days 148–151).
- Logistic regression and decision boundaries (Days 155–156).
- Python 3.11+ virtual environment.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (x86_64, aarch64)
- Windows (WSL2 / native PowerShell)

## Hardware requirements
- CPU: 1 core
- Memory: 512 MB RAM
- Disk: 50 MB for virtual environment

## Required software
- Python 3.11 or newer
- Virtual environment (`venv`)

## Free and open-source options
- Python standard library + NumPy / scikit-learn (free, open source).

## Installation
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

## File structure
```
day-169-support-vector-machines/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── svm_lib.py
│   └── test_svm_lib.py
├── examples/
│   ├── svm_lib.py
│   └── test_svm_lib.py
├── tests/
│   └── run_tests.sh
├── expected-output/
│   ├── FIELDS.md
│   ├── measured-values.txt
│   ├── test-run.txt
│   ├── examples-run.txt
│   └── starter-run.txt
├── troubleshooting.md
└── security.md
```

## How to run
Run the reference implementation:
```bash
python3 examples/svm_lib.py
```

## What the commands do
- `compute_rbf_kernel(X1, X2, gamma)` computes non-linear similarity Gram matrices.
- `LinearSVMScratch(C=1.0)` trains soft-margin linear classifiers via subgradient descent.

## Expected output
See `expected-output/test-run.txt` and `expected-output/measured-values.txt`.

## Validation steps
Execute the full test harness:
```bash
./tests/run_tests.sh
```

## Tests
Run pytest on the reference implementation:
```bash
pytest examples -v
```

## Cleanup
```bash
rm -rf .venv __pycache__ .pytest_cache
```

## Troubleshooting
Refer to [troubleshooting.md](troubleshooting.md).

## Security notes
Refer to [security.md](security.md).

## Extension exercises
1. Implement the Polynomial Kernel $K(x, z) = (x^T z + c)^d$ from scratch.
2. Implement Platt Scaling (logistic sigmoid fitting on SVM decision values) for probability calibration.
3. Benchmark runtime and memory scaling of `LinearSVC` vs `SVC(kernel='rbf')` as $N$ scales from 1,000 to 50,000.

## Navigation
- Previous lab (Week 24 Project): `../projects/week-24/`
- Next lab: `../day-170-feature-scaling-and-encoding/`
