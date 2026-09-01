# Troubleshooting: Day 232 - GPUs and AI Hardware

## Common Issues
1. **Intensity calculation discrepancy:**
   - Cause: Forgetting the factor of 2 in GEMM FLOPs ($2 N^3$ due to multiply and add).
   - Fix: Use $2 \times N^3$.
