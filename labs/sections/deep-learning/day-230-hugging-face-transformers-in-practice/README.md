# Lab: Day 230 -- Hugging Face Transformers in Practice

## Lesson
Day number: 230 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Hugging Face Transformers, Dynamic Padding, and Metrics.

## Purpose
Build and test a modular Hugging Face data pipeline and evaluation suite in PyTorch. Implement dynamic batch padding collation (`DataCollatorWithPadding`), construct attention masks, and build the metric compute engine (Accuracy, Precision, Recall, F1).

## Learning objectives
- Implement dynamic batch padding collation with `DataCollatorWithPadding`.
- Generate accurate binary attention masks for padded sequences.
- Implement classification evaluation metrics (Accuracy, Precision, Recall, F1).
- Verify dimensional compatibility across batched tensor pipelines.

## Prerequisites
- Day 229 (Decoder Models: The GPT Family).
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
- `starter/hugging_face_transformers_in_practice_lib.py`: Student scaffold file.
- `examples/hugging_face_transformers_in_practice_lib.py`: Complete reference implementation.
- `tests/test_hugging_face_transformers_in_practice_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/hugging_face_transformers_in_practice_lib.py
```

## What the commands do
- Evaluates dynamic batch collation across variable length sequences.
- Computes statistical accuracy and F1 metrics.
- Runs unit test assertions.

## Expected output
```
HF Demo: Collated Batch Shape = torch.Size([2, 5])
```

## Validation steps
1. Verify `MockDataCollatorWithPadding` pads batches strictly to the longest sequence in the batch.
2. Confirm `attention_mask` contains `1` for real tokens and `0` for pad tokens.
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
- **Attention mask shape mismatch:** Ensure attention mask has identical shape to `input_ids`.

## Security notes
All data collation computations execute locally in process memory.

## Extension exercises
1. Implement a Multi-Label F1 metric calculator.
2. Implement a Learning Rate Warmup schedule generator.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Hugging Face Transformers in Practice
- **Day number:** 230 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-230-hugging-face-transformers-in-practice
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-230-hugging-face-transformers-in-practice` when the site is running.
<!-- generated-links:end -->
