# Lab: Day 224 -- A Sentiment Analysis Project

## Lesson
Day number: 224 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: End-to-End Sentiment Analysis with Attention and Explainability.

## Purpose
Build and test an end-to-end sentiment classification pipeline in PyTorch. Implement the `BiLSTMAttentionSentiment` architecture, compute attention-pooled document vectors, and extract gradient-based token attribution saliency scores for individual review explanations.

## Learning objectives
- Implement bidirectional LSTM sequence encoding with learned attention pooling.
- Compute normalized attention weights and handle padding masks.
- Compute gradient saliency scores for token-level prediction explainability.
- Verify classification output dimensions and probability distributions.

## Prerequisites
- Day 223 (Text Classification with Embeddings).
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
- `starter/a_sentiment_analysis_project_lib.py`: Student scaffold file.
- `examples/a_sentiment_analysis_project_lib.py`: Complete reference implementation.
- `tests/test_a_sentiment_analysis_project_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/a_sentiment_analysis_project_lib.py
```

## What the commands do
- Evaluates BiLSTM attention forward passes over review batches.
- Calculates gradient saliency token attribution scores.
- Runs unit test assertions.

## Expected output
```
Sentiment Demo: Logits Shape = torch.Size([2, 2]), Saliency Shape = torch.Size([5])
```

## Validation steps
1. Verify `BiLSTMAttentionSentiment.forward` outputs logits of shape `(batch_size, num_classes)`.
2. Confirm `attn_weights` sum to 1.0 along the sequence dimension.
3. Ensure `explain_tokens` produces saliency vectors matching input token length.
4. Ensure all unit test assertions pass.

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
- **Gradients not tracked in explain_tokens:** Ensure embedding weights are detached and marked with `.requires_grad_(True)` before forward computation.

## Security notes
All sentiment processing and gradient calculations run locally in memory.

## Extension exercises
1. Implement temperature scaling to calibrate confidence probabilities.
2. Build an Integrated Gradients path integral calculation across $m=50$ interpolation steps.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Sentiment Analysis Project
- **Day number:** 224 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-224-a-sentiment-analysis-project
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-224-a-sentiment-analysis-project` when the site is running.
<!-- generated-links:end -->
