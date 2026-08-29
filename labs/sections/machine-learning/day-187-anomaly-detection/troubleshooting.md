# Troubleshooting: Day 187 - Anomaly Detection

## Common Issues
1. **Identical Scores Across Samples:**
   - Cause: Trees failed to split on feature ranges. Ensure min and max bounds are recomputed per node.
