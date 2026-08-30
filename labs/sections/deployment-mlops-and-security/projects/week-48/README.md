# Week 48 Capstone Project: Deployed AI System

## Project Overview
Build an end-to-end multi-replica deployed AI serving system in Python. This comprehensive system integrates:
1. **Paged KV Cache Management:** Non-contiguous block allocation with zero memory fragmentation.
2. **Continuous Iteration-Level Batching:** Dynamic request admission and departure eliminating idle GPU bubbles.
3. **AI Gateway with Least-Outstanding-Requests (LOR):** Concurrency-aware traffic distribution.
4. **Resilience & Circuit Breaking:** Graceful fallback generation upon replica health degradation.
5. **Telemetry & SRE Observability:** Measuring end-to-end throughput, Time-to-First-Token, and error rates.

## Architecture

```text
[Incoming User Traffic Burst]
             │
             ▼
[AI Gateway Proxy (LOR Balancing + Circuit Breaker)]
             ├── Worker 1 (Paged KV Cache + Continuous Batch)
             ├── Worker 2 (Paged KV Cache + Continuous Batch)
             └── Worker 3 (Paged KV Cache + Continuous Batch)
             │
             ▼
[Prometheus Telemetry & Health Monitoring]
```

## File Structure
- `starter/deployed_system.py`: Starter implementation skeleton
- `examples/deployed_system.py`: Verified reference implementation
- `tests/test_deployed_system.py`: Test suite
- `expected-output/`: Captured execution logs
- `requirements/requirements.txt`: Project dependencies

## How to run
```bash
python3 examples/deployed_system.py
```

## Expected output
```text
All 5 checks passed 100% with zero errors.
[GATEWAY] Initialized LOR proxy across 3 inference worker replicas.
[CONTINUOUS BATCHING] Processed 10 concurrent requests with zero GPU memory fragmentation.
[CIRCUIT BREAKER] Isolated degraded replica and routed traffic to healthy workers.
```

## Validation
Run test runner:
```bash
bash tests/run_tests.sh
```

## Verification Checklist
- [x] Correct paged memory allocation and freeing
- [x] Continuous batch execution across multiple replicas
- [x] LOR load balancing directing traffic to least-busy workers
- [x] Circuit breaker state transitions under simulated failures
- [x] Passing all 5 comprehensive unit tests
