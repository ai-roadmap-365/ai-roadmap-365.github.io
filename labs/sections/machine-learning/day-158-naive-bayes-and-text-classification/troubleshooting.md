# Troubleshooting Guide for Day 158

## Common Issues

### 1. Zero-Frequency Problem (Zero Likelihood)
- **Symptom:** A test document containing a single unseen word causes the entire class probability `P(x | y=c)` to become `0.0` (or `-inf` in log space).
- **Cause:** Without smoothing, `P(word | class) = 0 / N_c = 0`. Multiplying by zero annihilates all other word evidence.
- **Fix:** Always apply additive Laplace smoothing (`alpha=1.0`), ensuring unseen words have a non-zero baseline probability `alpha / (N_c + alpha * V)`.

### 2. Underflow from Multiplying Small Probabilities
- **Symptom:** Product of word probabilities `prod P(w_j | y)` underflows to floating point `0.0` on documents with >50 words.
- **Cause:** In float64, multiplying 50 probabilities of `10^-3` produces `10^-150`, risking underflow.
- **Fix:** Perform all computations in log-space: `log P(y) + sum (x_j * log P(w_j | y))`.
