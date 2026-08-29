# Troubleshooting: Day 189 - A Segmentation Study

## Common Issues
1. **Centroid Bias:**
   - Cause: Computing persona summaries on scaled data. Always use unscaled `X_raw`.
