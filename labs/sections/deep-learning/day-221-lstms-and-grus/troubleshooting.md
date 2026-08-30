# Troubleshooting: Day 221 - LSTMs and GRUs

## Common Issues
1. **Forget gate saturating at zero:**
   - Cause: Negative initial bias in forget gate.
   - Fix: Initialize forget gate bias to `+1.0`.
