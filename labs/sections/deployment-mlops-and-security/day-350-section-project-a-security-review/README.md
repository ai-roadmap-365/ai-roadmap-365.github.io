# Day 350 Lab: Section Project: A Security Review

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Section Project: A Security Review
- **Day number:** 350 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-350-section-project-a-security-review
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-350-section-project-a-security-review` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Unified Enterprise AI Security Review Platform in Python integrating threat modeling, prompt firewalls, PII token vaults, supply chain validation, adversarial red teaming, and executive compliance report generation.

## Learning objectives
- Orchestrate a multi-layer AI security gateway.
- Enforce in-memory PII tokenization and reversible detokenization.
- Intercept outbound canary token exfiltration.
- Audit model directories for SafeTensors compliance.
- Execute automated red team probes and calculate Attack Success Rates.

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
- `starter/security_review.py`: Starter implementation skeleton
- `examples/security_review.py`: Verified reference implementation
- `tests/test_security_review.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/security_review.py
```

## What the commands do
- Executes the full unified security audit suite, testing PII vaults, prompt firewalls, canary monitors, supply chain checks, and red team evaluations.

## Expected output
```text
{'application_name': 'Customer Copilot', 'overall_status': 'HARDENED_COMPLIANT', 'pii_vault_active': True, 'prompt_firewall_active': True, 'canary_monitor_active': True, 'attack_success_rate': 0.0, 'supply_chain_compliant': True}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Ingress PII sanitization and outbound detokenization
- Prompt firewall heuristic blocking and XML delimiter wrapping
- Outbound canary exfiltration dropping
- Model supply chain SafeTensors verification
- Full executive security report generation with zero ASR

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure PII sanitization is performed before XML delimiter wrapping in the ingress pipeline.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement automated PagerDuty incident alerting for canary leaks.

## Navigation
Day number: 350 of 365
