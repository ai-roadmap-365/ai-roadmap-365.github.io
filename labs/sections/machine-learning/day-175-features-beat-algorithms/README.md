# Lab 175: Proving "Features Beat Algorithms" via Controlled Empirical Benchmarking

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Features Beat Algorithms
- **Day number:** 175 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-175-features-beat-algorithms
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-175-features-beat-algorithms` when the site is running.
<!-- generated-links:end -->

## Purpose
Empirically demonstrate the Fundamental Theorem of Applied Machine Learning: prove that a simple, interpretable linear model trained on domain-engineered features outclasses models trained on raw un-engineered features, achieving higher accuracy, 100x lower latency, and complete explainability.

## Learning objectives
1. Construct controlled non-linear synthetic benchmarks comparing raw vs engineered representations.
2. Formulate domain physical ratios, cyclical temporal encodings, and interaction terms.
3. Quantify the Feature Return on Investment (ROI) metric: predictive gain per millisecond of compute.
4. Synthesize all Week 25 concepts (Scaling, Encoding, Selection, Pipelines, Imputation).
5. Analyze the technical debt of feature pipelines (Sculley et al., 2015).

## Prerequisites
- Days 169–174 (SVMs, Scaling, Feature Engineering, Selection, Pipelines, Imputation).
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
day-175-features-beat-algorithms/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── features_beat_algorithms_lib.py
│   └── test_features_beat_algorithms_lib.py
├── examples/
│   ├── features_beat_algorithms_lib.py
│   └── test_features_beat_algorithms_lib.py
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
python3 examples/features_beat_algorithms_lib.py
```

## What the commands do
- `engineer_domain_representation(...)` generates rich physical/temporal features.
- `benchmark_raw_vs_engineered(...)` runs a controlled head-to-head empirical comparison.

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
1. Compare an engineered Ridge model against an un-engineered 5-layer PyTorch Multi-Layer Perceptron (MLP) on training time, inference latency, and RMSE.
2. Build an automated feature degradation monitor that triggers alerts when feature distribution drift occurs in production.
3. Conduct an ablation study measuring the marginal R2 contribution of each engineered feature individually.

## Navigation
- Previous lab: `../day-174-handling-missing-data/`
- Next lab (Weekly Project): `../projects/week-25/`
