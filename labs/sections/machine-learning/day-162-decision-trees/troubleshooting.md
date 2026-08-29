# Troubleshooting Guide for Day 162

## Common Issues

### 1. Zero Division in Entropy with Zero Probability
- **Symptom:** `RuntimeWarning: divide by zero encountered in log2` returning `NaN`.
- **Cause:** Computing `0.0 * np.log2(0.0)`.
- **Fix:** Clip probabilities `np.clip(p, 1e-15, 1.0)` or filter `p > 0` before computing entropy.

### 2. Infinite Recursion / Maximum Recursion Depth Exceeded
- **Symptom:** `RecursionError: maximum recursion depth exceeded while calling a Python object`.
- **Cause:** A candidate split produces empty child partitions (`n_l == 0` or `n_r == 0`), causing infinite recursive loops.
- **Fix:** Enforce `if n_l == 0 or n_r == 0: continue` during threshold evaluation and base-case termination when `depth >= max_depth`.
