# Troubleshooting: Day 185 - Principal Component Analysis

## Common Issues
1. **Uncentered Data Distortions:**
   - Cause: Forgetting to subtract column means before running SVD.
   - Fix: Apply `X_centered = X - self.mean_`.
