# Troubleshooting - Day 290
1. **Type Coercion Failure:** Verify that target types in the schema match standard JSON types (`string`, `integer`, `number`, `boolean`).
2. **Idempotency Miss:** Ensure dictionary arguments are sorted before hashing to maintain deterministic keys.
