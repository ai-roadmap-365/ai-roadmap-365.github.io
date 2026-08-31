# Day 337 Lab: Deploying to a Cloud Service

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Deploying to a Cloud Service
- **Day number:** 337 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-337-deploying-to-a-cloud-service
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-337-deploying-to-a-cloud-service` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Cloud Deployment Orchestration Simulator in Python managing Blue-Green revisions, automated health check verification, zero-downtime cutovers, and rollback protection.

## Learning objectives
- Track Blue-Green revision states and traffic allocation.
- Execute health verification probes prior to cutover.
- Shift traffic with zero downtime upon successful validation.
- Abort cutover and preserve active traffic upon failure.

## Prerequisites
- Python 3.10+ installed
- pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, pytest

## Free and open-source options
- Python Standard Library, Pytest

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/cloud_deployment.py`: Starter implementation skeleton
- `examples/cloud_deployment.py`: Verified reference implementation
- `tests/test_cloud_deployment.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/cloud_deployment.py
```

## What the commands do
- Executes Blue-Green deployments, validates health checks, and tests rollbacks.

## Expected output
```text
{'status': 'DEPLOYMENT_SUCCESS', 'active_env': 'GREEN', 'deployed_image': 'v2.0.0', 'timestamp': 1788138002.104724}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Initial state with Blue active at 100% traffic
- Successful deployment to Green with full traffic cutover
- Subsequent deployment flipping traffic back to Blue
- Failed health check aborting deployment and preserving active traffic
- Deployment history audit logging

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure traffic percentages sum to 100%.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement a progressive canary rollout state machine.

## Navigation
Day number: 337 of 365
