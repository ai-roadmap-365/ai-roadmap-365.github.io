# Security Considerations - Day 290
1. **Side-Effect Protection:** Mutating actions require idempotency verification to prevent duplicate execution during network retries.
2. **Schema Sanitization:** Unregistered parameters are stripped before function execution to prevent unauthorized parameter pollution.
