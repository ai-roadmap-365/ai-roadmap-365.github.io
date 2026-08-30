# Lab: Day 254 -- The OpenAI-Compatible Ecosystem

## Lesson
Day number: 254 of 365.
Course: Course06-SS02 (LLMs and Generative AI - LLM APIs).
Topic: The OpenAI-Compatible Ecosystem, /v1/chat/completions, and Multi-Provider Routing.

## Purpose
Build and test an extensible Multi-Provider OpenAI-Compatible Router in Python. Configure tiered provider priority lists, execute automated failover on simulated network timeouts, and measure routing latencies.

## Learning objectives
- Structure API requests using the standard OpenAI `/v1/chat/completions` specification.
- Redirect client requests using custom `base_url` endpoints.
- Implement automated fallback failover across tiered model hosts.
- Benchmark provider latency and track routing telemetry.

## Prerequisites
- Day 253 (First Calls to the Claude API).
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
Python and standard time/typing modules are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/the_openai_compatible_ecosystem_lib.py`: Student scaffold file.
- `examples/the_openai_compatible_ecosystem_lib.py`: Complete reference implementation.
- `tests/test_the_openai_compatible_ecosystem_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/the_openai_compatible_ecosystem_lib.py
```

## What the commands do
- Registers providers with priority ratings.
- Dispatches chat completion request.
- Runs unit test assertions.

## Expected output
```
Router Demo Executed. Routed provider: vLLM_Primary
```

## Validation steps
1. Verify priority sorting routes to lowest priority integer first.
2. Confirm failed primary routes failover to secondary provider.
3. Validate empty provider list raises ValueError.
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
- **All providers failing:** Verify provider names do not contain 'fail' unless simulating errors.

## Security notes
All routing logic executes locally in memory.

## Extension exercises
1. Implement a rolling latency load balancer.
2. Build an automated circuit breaker with 60-second recovery timeouts.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The OpenAI-Compatible Ecosystem
- **Day number:** 254 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-254-the-openai-compatible-ecosystem
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-254-the-openai-compatible-ecosystem` when the site is running.
<!-- generated-links:end -->
