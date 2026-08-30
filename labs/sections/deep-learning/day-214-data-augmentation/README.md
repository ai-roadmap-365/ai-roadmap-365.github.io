# Lab: Day 214 -- Data Augmentation

## Lesson
Day number: 214 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Data Augmentation in Computer Vision.

## Purpose
Build and test a modern Computer Vision Data Augmentation library in PyTorch. Implement mathematical algorithms for MixUp convex linear blending and CutMix spatial patch masking from first principles, verify label interpolation properties, and construct stochastic training transform pipelines.

## Learning objectives
- Implement MixUp convex interpolation across image tensors and one-hot target vectors.
- Implement CutMix bounding box patch generation and exact area proportion calculation.
- Construct stochastic training vs deterministic validation transform pipelines.
- Verify label probability conservation and manifold smoothing.

## Prerequisites
- Day 213 (Transfer Learning).
- Python 3.11+ with PyTorch and torchvision.

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
PyTorch and torchvision are free and open-source under modified BSD licenses.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/data_augmentation_lib.py`: Student scaffold file.
- `examples/data_augmentation_lib.py`: Complete reference implementation.
- `tests/test_data_augmentation_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/data_augmentation_lib.py
```

## What the commands do
- Applies MixUp and CutMix algorithms across synthetic image batches.
- Computes soft probability label distributions.
- Validates tensor shapes and target conservation.

## Expected output
```
Augmentation Demo: MixUp Shape = torch.Size([4, 3, 32, 32]), CutMix Shape = torch.Size([4, 3, 32, 32])
```

## Validation steps
1. Confirm that `apply_mixup` produces soft probability rows summing to 1.0.
2. Confirm that `apply_cutmix` computes actual area ratios accurately.
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
- **Dimensions Error in CutMix:** Verify `rand_bbox` clips coordinates within `[0, W]` and `[0, H]`.

## Security notes
All augmentations execute locally in CPU/GPU memory without external network calls.

## Extension exercises
1. Implement Test-Time Augmentation (TTA) averaging across multiple augmented test copies.
2. Implement Mosaic 4-image grid augmentation.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Data Augmentation
- **Day number:** 214 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-214-data-augmentation
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-214-data-augmentation` when the site is running.
<!-- generated-links:end -->
