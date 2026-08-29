# Troubleshooting: Day 200 - Backpropagation

## Common Issues
1. **Gradient Dimension Mismatch:**
   - Cause: Inverted matrix multiplication during backward step.
   - Fix: Ensure dW is (dZ @ A_prev.T) and dA_prev is (W.T @ dZ).
