# Lab: Day 219 -- Word Embeddings

## Lesson
Day number: 219 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Word Embeddings and Vector Semantics.

## Purpose
Build and test a complete Word Embedding engine in PyTorch. Implement the Word2Vec Skip-Gram model architecture with Negative Sampling loss, evaluate cosine similarity metrics, and perform semantic vector arithmetic.

## Learning objectives
- Implement the Word2Vec Skip-Gram neural architecture with target and context embedding layers.
- Derive and compute Negative Sampling binary cross-entropy loss.
- Calculate cosine similarity across multi-dimensional embedding vectors.
- Validate semantic geometric properties in learned embedding spaces.

## Prerequisites
- Day 218 (Text Preprocessing and Tokenization).
- Python 3.11+ with PyTorch and NumPy.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 1 GB RAM.
- 100 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
PyTorch is open-source software maintained by the Linux Foundation under a modified BSD license.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/word_embeddings_lib.py`: Student scaffold file.
- `examples/word_embeddings_lib.py`: Complete reference implementation.
- `tests/test_word_embeddings_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/word_embeddings_lib.py
```

## What the commands do
- Initializes target and context embedding tables in PyTorch.
- Computes negative sampling loss over sample center, context, and noise batches.
- Runs cosine similarity assertions across orthogonal and parallel vectors.

## Expected output
```
Embedding Demo: Loss = 3.4716, Cosine Sim = 0.1245
```

## Validation steps
1. Verify `SkipGramNegativeSampling.forward` returns a scalar positive loss tensor.
2. Confirm `compute_cosine_similarity` returns 1.0 for identical vectors and 0.0 for orthogonal vectors.
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
- **Negative Loss Values:** Ensure you are minimizing `- (pos_loss + neg_loss)`.

## Security notes
All neural embedding operations execute locally on CPU or local GPU acceleration.

## Extension exercises
1. Implement GloVe weighted co-occurrence matrix regression loss.
2. Implement FastText character n-gram hashing embedding layer.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Word Embeddings
- **Day number:** 219 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-219-word-embeddings
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-219-word-embeddings` when the site is running.
<!-- generated-links:end -->
