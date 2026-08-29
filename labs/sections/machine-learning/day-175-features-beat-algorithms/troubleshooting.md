# Troubleshooting Guide for Day 175

## Common Issues

### 1. The "Hidden Technical Debt" Anti-Pattern (CMLC)
- **Symptom:** Adding 50 experimental features creates an unmaintainable codebase where changing one feature breaks 10 downstream models ("Changing Anything Changes Everything").
- **Cause:** Lack of modular feature store definitions and feature documentation.
- **Fix:** Track every feature's mathematical definition, upstream lineage, and data dependencies in a standardized feature store schema.

### 2. Over-Engineering on Pure Noise
- **Symptom:** Complex engineered features score 0.99 in training but fail to generalize to validation data.
- **Cause:** Creating high-order polynomial combinations without domain hypothesis validation.
- **Fix:** Use Boruta or RFECV feature selection inside cross-validation to prune uninformative engineered interactions.
