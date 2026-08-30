# Lab: Day 251 -- Prompt Injection and Safe Prompting

## Lesson
Day number: 251 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Prompt Injection, Jailbreak Defense, and Multi-Tier Security Firewalls.

## Purpose
Build and test a production-grade Prompt Security Firewall and payload sanitization pipeline in Python. Implement ingress heuristic detection and XML tag escaping, configure Canary Token leakage inspection, and block markdown image exfiltration payloads.

## Learning objectives
- Distinguish between direct jailbreaks and indirect data poisoning injections.
- Enforce XML delimiter tag escaping to block parameter breakout exploits.
- Implement Canary Token leakage detection in egress streams.
- Block markdown image exfiltration vectors.

## Prerequisites
- Day 250 (Prompt Patterns and Templates).
- Python 3.11+ with Pytest.

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
Python regex and standard security libraries are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/prompt_injection_and_safe_prompting_lib.py`: Student scaffold file.
- `examples/prompt_injection_and_safe_prompting_lib.py`: Complete reference implementation.
- `tests/test_prompt_injection_and_safe_prompting_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/prompt_injection_and_safe_prompting_lib.py
```

## What the commands do
- Sanitizes untrusted ingress prompts.
- Scans egress outputs for canary leaks and image tags.
- Runs unit test assertions.

## Expected output
```
Firewall Demo Executed. Ingress Suspicious: True
```

## Validation steps
1. Verify `sanitize_ingress` flags injection keywords.
2. Confirm delimiter tag escaping replaces closing tags with `&lt;` entities.
3. Validate Canary token detection blocks exfiltration.
4. Ensure all unit test assertions pass.

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
- **False positive heuristic triggers:** Refine regex patterns with strict word boundary tokens.

## Security notes
Defense-in-depth requires combining regex filters, XML sandboxing, and output scanning.

## Extension exercises
1. Implement a Base64 adversarial prompt de-obfuscator.
2. Build an automated red-teaming benchmark suite for OWASP Top 10 LLM risks.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Prompt Injection and Safe Prompting
- **Day number:** 251 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-251-prompt-injection-and-safe-prompting
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-251-prompt-injection-and-safe-prompting` when the site is running.
<!-- generated-links:end -->
