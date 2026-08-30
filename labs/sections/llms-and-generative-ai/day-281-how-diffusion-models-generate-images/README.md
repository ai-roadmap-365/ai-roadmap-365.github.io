# Day 281 Lab: Diffusion Noise Scheduler and Reverse Sampler

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** How Diffusion Models Generate Images
- **Day number:** 281 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-281-how-diffusion-models-generate-images
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-281-how-diffusion-models-generate-images` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a vectorized Gaussian Diffusion noise scheduler in Python and NumPy implementing closed-form forward noise injection ($q(x_t | x_0)$) and iterative reverse Markov denoising ($p_\theta(x_{t-1} | x_t)$).

## Learning objectives
- Calculate cumulative variance products ($\bar{\alpha}_t = \prod \alpha_i$) for linear and cosine schedules.
- Implement closed-form forward diffusion: $x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1 - \bar{\alpha}_t} \epsilon$.
- Implement single-step reverse denoising updates.
- Execute full reverse sampling trajectories from pure Gaussian noise.

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
- `starter/diffusion_scheduler.py`: Starter implementation skeleton
- `examples/diffusion_scheduler.py`: Verified reference implementation
- `tests/test_diffusion_scheduler.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/diffusion_scheduler.py
```

## What the commands do
- Evaluates forward noising and reverse sampling math across 100 timesteps.

## Expected output
```text
[DIFFUSION SCHEDULER] Timesteps: 1000 | Schedule: Linear (beta: 0.0001 -> 0.02)
[FORWARD DIFFUSION] Injected Noise at Timestep t=500: alpha_bar = 0.5012
[REVERSE SAMPLING] Successfully denoised from pure noise to reconstructed tensor.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Linear and cosine cumulative alpha decay
- Forward closed-form noising across arbitrary timesteps
- Reverse single-step Markov mean and variance computation
- Timestep index boundary checks

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure `expand_dims` matches the dimensionality of input sample tensors.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement DDIM deterministic non-Markovian sampling with sub-sequence strides.

## Navigation
Day number: 281 of 365
