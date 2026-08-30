# Lab: Day 216 -- Beyond Classification: Detection and Segmentation

## Lesson
Day number: 216 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Object Detection and Semantic Segmentation Algorithms in PyTorch.

## Purpose
Build and test a modular dense spatial computer vision library in PyTorch. Implement Intersection over Union (IoU) bounding box calculations, Non-Maximum Suppression (NMS) candidate filtering, and soft Dice Loss for imbalanced segmentation masks.

## Learning objectives
- Implement bounding box Intersection over Union (IoU) from coordinate geometry.
- Implement greedy Non-Maximum Suppression (NMS) to eliminate duplicate detection proposals.
- Implement soft Dice Loss for binary semantic segmentation masks.
- Validate spatial prediction accuracy on multi-object test batches.

## Prerequisites
- Day 215 (Training a Vision Model End to End).
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
- `starter/beyond_classification_detection_and_segmentation_lib.py`: Student scaffold file.
- `examples/beyond_classification_detection_and_segmentation_lib.py`: Complete reference implementation.
- `tests/test_beyond_classification_detection_and_segmentation_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/beyond_classification_detection_and_segmentation_lib.py
```

## What the commands do
- Computes IoU between overlapping bounding boxes.
- Filters redundant candidate proposals using NMS.
- Runs validation unit tests.

## Expected output
```
Dense Vision Demo: IoU = 0.3333, NMS Kept Indices = [0, 2]
```

## Validation steps
1. Verify `calculate_iou` yields 1.0 for identical boxes and 0.0 for disjoint boxes.
2. Confirm `apply_nms` removes overlapping duplicate boxes above the threshold.
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
- **Negative IoU Values:** Ensure coordinate differences are clamped with `max(0.0, ...)`.

## Security notes
All spatial algorithms execute locally in CPU memory without external network calls.

## Extension exercises
1. Implement Generalized IoU (GIoU) and Complete IoU (CIoU) bounding box loss functions.
2. Implement Mean Average Precision (mAP@0.5) evaluator over detection batches.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Beyond Classification: Detection and Segmentation
- **Day number:** 216 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-216-beyond-classification-detection-and-segmentation
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-216-beyond-classification-detection-and-segmentation` when the site is running.
<!-- generated-links:end -->
