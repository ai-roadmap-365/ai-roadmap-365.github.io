# Week 49 Capstone Project: A Monitored Production AI Deployment Platform

## Project Overview
Build an end-to-end production AI operations platform orchestrating dynamic batching, OpenTelemetry percentiles, PII sanitization, multi-tenant cost attribution, and automated circuit breaker rollbacks.

## System Architecture
The platform integrates:
1. **Security & Ingress Layer:** In-memory regex PII sanitizer for SSNs, emails, and credit cards; W3C trace ID generation.
2. **Dynamic Routing Layer:** Deterministic user hashing (`hash(user_id) % 100`) for progressive canary rollouts.
3. **Serving & Batching Layer:** Dynamic server-side batching simulator with queue delay timeouts and VRAM bounds.
4. **Observability & Analytics Layer:** Rolling percentile latency engine (P50, P95, P99) and ClickHouse-style multi-tenant token billing ledger.
5. **Self-Healing Layer:** Automated circuit breaker tripping and reverting to baseline upon error spikes.

## Prerequisites
- Python 3.10+ installed
- pytest, numpy installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## How to run
```bash
python3 examples/production_ai_ops.py
```

## Expected output
```text
All 5 checks passed 100% with zero errors.
[PLATFORM] Initialized Unified Monitored AI Platform (Canary: 20%, Error Threshold: 5.0%).
[INGRESS] Sanitized PII; processed request under trace_id=3a9b1c2d...
[OBSERVABILITY] Generated metrics report: P50=120ms, P95=145ms, Error Rate=0.0%.
[COST LEDGER] Recorded $0.0005 attributed spend for tenant_acme.
[AUTOMATED CIRCUIT BREAKER] Tripped circuit upon error spike; reverted traffic to BASELINE_V1.
```

## Validation
Run test runner:
```bash
bash tests/run_tests.sh
```

## Verification Checklist
- [x] In-memory PII sanitization active
- [x] Deterministic user hashing verified
- [x] Percentile latencies computed accurately
- [x] Multi-tenant token ledger aggregated
- [x] Automated circuit breaker rollback verified
