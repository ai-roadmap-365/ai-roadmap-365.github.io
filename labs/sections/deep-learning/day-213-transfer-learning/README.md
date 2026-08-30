# Lab: Day 213 -- Transfer Learning

## Lesson
Day number: 213 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Transfer Learning and Fine-Tuning in PyTorch.

## Purpose
Build and test a modular Transfer Learning architecture in PyTorch. Implement parameter freezing routines with `requires_grad`, replace classification heads for custom target datasets, configure differential layer-wise learning rates, and verify that frozen backbones receive zero gradient updates during backward propagation.

## Learning objectives
- Freeze and unfreeze parameter subsets in PyTorch vision models.
- Replace fully connected heads to support arbitrary target classes.
- Verify gradient isolation during backpropagation.
- Configure multi-group differential learning rate optimizers.

## Prerequisites
- Day 212 (CNN Architectures).
- Python 3.11+ with PyTorch.

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
PyTorch is free and open-source under the modified BSD license.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/transfer_learning_lib.py`: Student scaffold file.
- `examples/transfer_learning_lib.py`: Complete reference implementation.
- `tests/test_transfer_learning_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/transfer_learning_lib.py
```

## What the commands do
- Instantiates a TransferVisionModel with a frozen backbone.
- Evaluates forward pass and counts frozen vs trainable parameters.
- Validates gradient isolation and differential optimizer grouping.

## Expected output
```
Transfer Demo: Out = torch.Size([2, 5]), Frozen = 5120, Trainable = 613
```

## Validation steps
1. Verify that `requires_grad=False` parameters receive `None` gradients during backprop.
2. Confirm that newly added classification heads receive valid gradients.
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
- **Backbone Receives Gradients:** Ensure `requires_grad = False` is set before invoking the optimizer.

## Security notes
All neural models execute in local system memory without external telemetry.

## Extension exercises
1. Implement embedding caching: extract backbone feature vectors to disk and train a linear classifier in 1 second.
2. Implement gradual unfreezing across successive training epochs.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Transfer Learning
- **Day number:** 213 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-213-transfer-learning
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-213-transfer-learning` when the site is running.
<!-- generated-links:end -->
