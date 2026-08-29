# Lab 158: Naive Bayes and Text Classification from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Naive Bayes and Text Classification
- **Day number:** 158 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-158-naive-bayes-and-text-classification
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-158-naive-bayes-and-text-classification` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a complete text classification pipeline from scratch: raw text tokenization, vocabulary indexing, Bag-of-Words feature matrix generation, and a vectorized Multinomial Naive Bayes classifier with Laplace smoothing.

## Learning objectives
1. Implement regular expression text tokenization and vocabulary dictionary mapping.
2. Construct sparse/dense Bag-of-Words (BOW) document-term count matrices.
3. Formulate class priors and conditional feature log-likelihoods.
4. Implement additive Laplace smoothing (`alpha`) to eliminate zero-frequency multiplication failures.
5. Benchmark scratch Multinomial Naive Bayes against scikit-learn on spam filtering tasks.

## Prerequisites
- Conditional probability and Bayes' theorem (Day 115).
- Python strings, dictionaries, and regular expressions (`re`).
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
day-158-naive-bayes-and-text-classification/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── nb_lib.py
│   └── test_nb_lib.py
├── examples/
│   ├── nb_lib.py
│   └── test_nb_lib.py
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
python3 examples/nb_lib.py
```

## What the commands do
- `tokenize(text)` extracts clean word tokens.
- `build_vocabulary(corpus)` constructs the indexed vocabulary.
- `text_to_bow(corpus, vocab)` builds the document-term matrix.
- `ScratchMultinomialNB(alpha=1.0).fit(X, y)` computes smoothed log likelihoods.

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
1. Implement Bernoulli Naive Bayes (`BernoulliNB`) for binary word occurrence vectors.
2. Implement Gaussian Naive Bayes (`GaussianNB`) with mean and variance estimation for continuous tabular features.
3. Add TF-IDF weighting (`term frequency * inverse document frequency`) into the Bag-of-Words matrix.

## Navigation
- Previous lab: `../day-157-k-nearest-neighbors/`
- Next lab: `../day-159-precision-recall-roc-and-choosing-thresholds/`
