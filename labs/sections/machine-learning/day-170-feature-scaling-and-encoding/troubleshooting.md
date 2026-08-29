# Troubleshooting Guide for Day 170

## Common Issues

### 1. Target Leakage in Mean Target Encoding
- **Symptom:** Target encoding feature gives 99% training score but fails catastrophically on test data.
- **Cause:** Calculating target means across the entire dataset without cross-validation splits.
- **Fix:** Always compute target encodings strictly out-of-fold (OOF) across $K$ folds with smoothing parameter $m$.

### 2. Dimension Explosion with High-Cardinality One-Hot Encoding
- **Symptom:** Memory exhausted when one-hot encoding a `ZipCode` feature with 40,000 unique values.
- **Cause:** One-hot encoding creates 40,000 sparse columns, triggering compute starvation.
- **Fix:** Use Target Encoding, Frequency Encoding, or Feature Hashing for high-cardinality nominal features ($k > 15$).
