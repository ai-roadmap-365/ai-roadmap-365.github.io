# Security and Privacy Notes for Day 166

- **Compute Exhaustion Vulnerability:** Untrusted user input defining large grid dimensions can trigger Denial of Service via compute starvation. Enforce hard limits on total search trials (`max_iter <= 100`).
- **Local Sandbox:** All cross-validation loops execute locally on CPU threads.
