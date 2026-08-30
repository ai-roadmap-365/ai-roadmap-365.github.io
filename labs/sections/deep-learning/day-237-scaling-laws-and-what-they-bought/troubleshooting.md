# Troubleshooting: Day 237 - Scaling Laws and What They Bought Us

## Common Issues
1. **Exponentiation overflow in power law:**
   - Cause: Passing parameters in billions directly to power function.
   - Fix: Use raw parameter counts $N$ and $D$.
