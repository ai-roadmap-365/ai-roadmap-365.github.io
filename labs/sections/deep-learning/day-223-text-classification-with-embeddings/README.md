# Lab: Day 223 -- Text Classification with Embeddings

## Lesson
Day number: 223 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Neural Text Classification Architectures.

## Purpose
Build and test modular neural text classification architectures in PyTorch. Implement the fast `EmbeddingBagClassifier` with fused average pooling, build the Yoon Kim `TextCNN` multi-scale 1D convolution model with max-over-time pooling, and verify classification logits across variable-length text batches.

## Learning objectives
- Implement `nn.EmbeddingBag` document representations with fused mean reduction.
- Construct the Yoon Kim TextCNN architecture with parallel multi-scale 1D convolutions.
- Implement 1-max pooling over time to achieve variable-length sequence invariance.
- Verify dimensional compatibility and classification output shapes.

## Prerequisites
- Day 222 (Sequence-to-Sequence and Early Attention).
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
- `starter/text_classification_with_embeddings_lib.py`: Student scaffold file.
- `examples/text_classification_with_embeddings_lib.py`: Complete reference implementation.
- `tests/test_text_classification_with_embeddings_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/text_classification_with_embeddings_lib.py
```

## What the commands do
- Executes forward passes through EmbeddingBag and TextCNN models.
- Verifies output tensor dimensions and multi-scale feature pooling.
- Runs unit test assertions.

## Expected output
```
Classification Demo: EB Shape = torch.Size([2, 2]), CNN Shape = torch.Size([2, 2])
```

## Validation steps
1. Verify `EmbeddingBagClassifier.forward` outputs a tensor of shape `(batch_size, num_classes)`.
2. Confirm `TextCNN.forward` outputs a tensor of shape `(batch_size, num_classes)`.
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
- **Input sequence too short for TextCNN:** Ensure sentence length is at least as large as the largest convolution kernel size ($k=3$ or $k=4$).

## Security notes
All classification models execute in local memory.

## Extension exercises
1. Implement a multi-channel TextCNN with static and fine-tuned embeddings.
2. Implement depthwise separable 1D convolutions to reduce parameters.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Text Classification with Embeddings
- **Day number:** 223 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-223-text-classification-with-embeddings
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-223-text-classification-with-embeddings` when the site is running.
<!-- generated-links:end -->
