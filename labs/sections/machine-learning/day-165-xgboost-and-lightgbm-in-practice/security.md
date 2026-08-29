# Security and Privacy Notes for Day 165

- **Missing Value Exploits:** Tree models learn dedicated default split branches for missing values (`NaN` paths). Ensure malicious actors cannot alter model routing by deliberately injecting missing values into payloads.
- **High-Performance Execution:** Compiled histogram algorithms execute locally with SIMD/AVX2 acceleration.
