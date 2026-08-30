# Troubleshooting: Day 233 - Mixed Precision and Performance

## Common Issues
1. **Scaler scale factor collapsing to zero:**
   - Cause: Consecutive NaN gradients without learning rate warmup.
   - Fix: Lower base learning rate and add warmup.
