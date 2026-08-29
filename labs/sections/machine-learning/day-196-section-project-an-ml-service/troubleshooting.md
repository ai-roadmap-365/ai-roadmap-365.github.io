# Troubleshooting: Day 196 - Section Project: An ML Service

## Common Issues
1. **Unconfigured Reference Data:**
   - Cause: Calling `evaluate_feature_drift_psi()` before `set_reference_data()`.
   - Fix: Initialize reference baseline dataset before evaluating streaming drift.
