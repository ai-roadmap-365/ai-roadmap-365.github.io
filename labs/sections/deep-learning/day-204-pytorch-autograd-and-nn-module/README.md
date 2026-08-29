# Lab: Day 204 -- PyTorch: autograd and nn.Module

## Lesson
Day number: 204 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: PyTorch autograd and nn.Module.

## Purpose
Master PyTorch automatic differentiation and neural network abstraction. Build a custom `torch.nn.Module` architecture, inspect computational graph `grad_fn` nodes, manage parameter isolation and gradient zeroing, serialize state dictionaries, and execute standardized training iterations.

## Learning objectives
- Construct object-oriented neural networks by subclassing `torch.nn.Module`.
- Inspect and verify autograd computation graph nodes (`grad_fn`, `requires_grad`).
- Implement the canonical 5-step PyTorch training iteration.
- Serialize and restore model checkpoints using `state_dict()`.

## Prerequisites
- Day 202-203 (PyTorch Tensors, Training MNIST from Scratch).
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
- `starter/pytorch_autograd_and_nn_module_lib.py`: Student scaffold file.
- `examples/pytorch_autograd_and_nn_module_lib.py`: Complete reference implementation.
- `tests/test_pytorch_autograd_and_nn_module_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/pytorch_autograd_and_nn_module_lib.py
```

## What the commands do
- Instantiates a two-layer `DeepClassifier` model.
- Executes multiple training steps with autograd backpropagation.
- Validates parameter reduction and loss convergence.

## Expected output
```
DeepClassifier Params: 101770, Initial Loss: 2.3412, Final Loss: 0.4120
```

## Validation steps
1. Verify that the model contains 101,770 trainable parameters.
2. Confirm that `loss.backward()` populates `.grad` attributes on all weights.
3. Ensure that `state_dict` correctly loads across model instances.

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
- **Gradient Not Updating:** Ensure `optimizer.step()` is called after `loss.backward()`.

## Security notes
All computations execute locally in memory on CPU hardware.

## Extension exercises
1. Implement a custom layer subclassing `nn.Module` that applies learned affine scaling.
2. Add weight freezing utility to freeze specific layers during transfer learning.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** PyTorch: autograd and nn.Module
- **Day number:** 204 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-204-pytorch-autograd-and-nn-module
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-204-pytorch-autograd-and-nn-module` when the site is running.
<!-- generated-links:end -->
