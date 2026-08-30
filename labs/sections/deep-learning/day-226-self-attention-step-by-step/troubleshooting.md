# Troubleshooting: Day 226 - Self-Attention, Step by Step

## Common Issues
1. **Stride mismatch error in tensor reshape:**
   - Cause: Reshaping transposed tensor directly.
   - Fix: Use `.contiguous().view(...)`.
