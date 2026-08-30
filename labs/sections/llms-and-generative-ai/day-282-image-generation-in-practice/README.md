# Day 282 Lab: Latent Diffusion Pipeline & CFG Simulator

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Image Generation in Practice
- **Day number:** 282 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-282-image-generation-in-practice
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-282-image-generation-in-practice` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Latent Diffusion pipeline simulator in Python implementing Classifier-Free Guidance (CFG), negative prompt steering, and VAE 8x spatial autoencoder compression.

## Learning objectives
- Implement Classifier-Free Guidance: $\hat{\epsilon} = \epsilon_{\text{uncond}} + s \cdot (\epsilon_{\text{cond}} - \epsilon_{\text{uncond}})$.
- Apply negative prompt algebraic steering.
- Simulate 8x VAE spatial downsampling and decoding.
- Calculate spatial compression metrics (48x numerical reduction).

## Prerequisites
- Python 3.10+ installed
- NumPy and pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, numpy, pytest

## Free and open-source options
- Python Standard Library, NumPy

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/latent_pipeline.py`: Starter implementation skeleton
- `examples/latent_pipeline.py`: Verified reference implementation
- `tests/test_latent_pipeline.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/latent_pipeline.py
```

## What the commands do
- Evaluates CFG extrapolation and VAE decoding on 4D image arrays.

## Expected output
```text
[CFG] Applied scale s=7.5 | Output Norm: 9.61
[VAE] Decoded (64, 64, 4) Latent to (512, 512, 3) RGB | Compression: 48.0x
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Linear CFG noise vector extrapolation
- Scale 1.0 identity passthrough
- Negative prompt steering math
- VAE 8x spatial dimension transformations

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Check that RGB outputs clamp to $[0, 255]$ before uint8 casting.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement dynamic thresholding to prevent color burning at high guidance scales ($s > 15$).

## Navigation
Day number: 282 of 365
