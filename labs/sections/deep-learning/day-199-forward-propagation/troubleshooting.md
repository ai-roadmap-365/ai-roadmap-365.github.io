# Troubleshooting: Day 199 - Forward Propagation

## Common Issues
1. **Matrix Incompatible Shapes:**
   - Cause: Layer weights dimension does not match input activation dimension.
   - Fix: Ensure W has shape (out_features, in_features).
