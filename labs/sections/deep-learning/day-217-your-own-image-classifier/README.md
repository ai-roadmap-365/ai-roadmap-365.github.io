# Lab: Day 217 -- Your Own Image Classifier

## Lesson
Day number: 217 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Custom Image Classifier Engineering and Error Diagnostics.

## Purpose
Build and test a custom image classifier auditing toolkit in PyTorch. Implement perceptual hashing (pHash) near-duplicate detection, construct an Error-Case Gallery generator to surface high-confidence misclassifications, and diagnose failure modes.

## Learning objectives
- Implement perceptual hashing (pHash) and Hamming distance deduplication.
- Generate an Error-Case Gallery sorting prediction failures by confidence.
- Categorize model errors into label noise, optical artifacts, and taxonomic ambiguity.
- Validate classification robustness on synthetic multi-class distributions.

## Prerequisites
- Day 216 (Beyond Classification: Detection and Segmentation).
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
PyTorch and NumPy are free and open-source under modified BSD licenses.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/your_own_image_classifier_lib.py`: Student scaffold file.
- `examples/your_own_image_classifier_lib.py`: Complete reference implementation.
- `tests/test_your_own_image_classifier_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/your_own_image_classifier_lib.py
```

## What the commands do
- Computes pHash Hamming distance across test images.
- Generates a sorted Error-Case Gallery from sample logits.
- Runs validation unit tests.

## Expected output
```
Classifier Audit Demo: pHash Dist = 0, Top Error = Peppermint (Conf: 0.97)
```

## Validation steps
1. Verify `calculate_simple_phash` produces 64-bit strings and 0 distance for identical images.
2. Confirm `generate_error_gallery` ranks the highest-confidence misclassification first.
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
- **Empty Error Gallery:** If no errors occurred, check that validation predictions contain at least one misclassified sample.

## Security notes
All dataset deduplication and auditing algorithms execute locally in memory.

## Extension exercises
1. Implement Grad-CAM activation mapping overlays for error gallery samples.
2. Export the fine-tuned classifier to ONNX and benchmark INT8 quantization latency.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Your Own Image Classifier
- **Day number:** 217 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-217-your-own-image-classifier
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-217-your-own-image-classifier` when the site is running.
<!-- generated-links:end -->
