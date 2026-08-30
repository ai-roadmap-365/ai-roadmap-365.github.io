# Troubleshooting: Day 225 - “Attention Is All You Need”

## Common Issues
1. **Dimension error in batched matmul:**
   - Cause: Calling `.T` on 4D tensor.
   - Fix: Use `.transpose(-2, -1)`.
