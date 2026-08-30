# Week 46 Capstone Project: Full-Stack AI App

## Project Overview
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

Build a production-grade **Full-Stack AI Application Suite** that unites all Week 46 concepts:
1. **Multi-Tenant Auth & Quotas:** Authenticate API keys via SHA-256 hashes, enforce dual RPM and TPM rate limits, and isolate tenant workspaces.
2. **Multi-Tier Latency Optimization:** Integrate Tier 1 Exact Hash caching and Tier 2 Semantic Vector caching to serve repeat queries instantly at $0.00 cost.
3. **Two-Phase Token Billing:** Place credit pre-authorization holds prior to model execution, settle exact token charges upon completion, and release unused holds.
4. **Resilient Vendor Gateway & Failover:** Route requests across an ordered multi-provider cascade (Claude 3.5 Sonnet -> GPT-4o -> Local vLLM), intercepting upstream errors and executing sub-second failover.
5. **Streaming Chat UX State Engine:** Manage optimistic user message rendering, streaming token aggregation, smart auto-scroll physics, and user abort controls.

## Project Requirements
1. **Multi-Tenant Gateway:** Register tenants, verify API keys, and enforce RPM/TPM limits.
2. **Multi-Tier Caching:** Support exact string and semantic vector cache hits.
3. **Two-Phase Credit Transactions:** Manage pre-auth holds and exact token settlements.
4. **Multi-Provider Failover:** Support automatic routing to backup replicas on primary failure.

## File Structure
- `starter/full_stack_ai_app_suite.py`: Starter implementation skeleton
- `examples/full_stack_ai_app_suite.py`: Complete verified reference solution
- `tests/test_full_stack_ai_app_suite.py`: Comprehensive test suite
- `expected-output/`: Verified execution logs

## How to Run
```bash
python3 examples/full_stack_ai_app_suite.py
```

## Validation
```bash
bash tests/run_tests.sh
```

## Expected output
```text
All 5 checks passed 100% with zero errors.
```

## Security Notes
Executes entirely in isolated local Python environment with zero production network access.
