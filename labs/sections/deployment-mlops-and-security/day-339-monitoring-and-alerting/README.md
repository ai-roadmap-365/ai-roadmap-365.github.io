# Day 339 Lab: Monitoring and Alerting

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Monitoring and Alerting
- **Day number:** 339 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-339-monitoring-and-alerting
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-339-monitoring-and-alerting` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an AI Observability and Alerting Engine in Python calculating rolling percentile latencies, evaluating SRE Golden Signals, and triggering actionable alerts.

## Learning objectives
- Record inference latency samples and error outcomes.
- Compute rolling percentiles (P50, P95, P99).
- Evaluate error rate percentages against SLA thresholds.
- Trigger structured critical alerts on SLA breaches.

## Prerequisites
- Python 3.10+ installed
- pytest, numpy installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, pytest, numpy

## Free and open-source options
- Python Standard Library, Pytest, NumPy

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/monitoring_alerting.py`: Starter implementation skeleton
- `examples/monitoring_alerting.py`: Verified reference implementation
- `tests/test_monitoring_alerting.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/monitoring_alerting.py
```

## What the commands do
- Evaluates percentile latency distributions and verifies alert trigger thresholds.

## Expected output
```text
All 5 checks passed 100% with zero errors.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Correct P50, P95, and P99 calculation on uniform and heavy-tailed samples
- Triggering HighTailLatencyP95 alert when threshold is exceeded
- Triggering HighInferenceErrorRate alert when error rate spikes
- Zero alert activation on healthy baseline traffic
- Graceful empty metrics handling

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure numpy is imported for percentile calculation.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement alert resolution cooldown hysteresis.

## Navigation
Day number: 339 of 365
