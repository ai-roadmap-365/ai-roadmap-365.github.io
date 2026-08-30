# Troubleshooting: Day 222 - Sequence-to-Sequence and Early Attention

## Common Issues
1. **Masked positions receiving non-zero attention:**
   - Cause: Mask value used is not negative enough before softmax.
   - Fix: Use `energy.masked_fill(mask == 0, -1e9)`.
