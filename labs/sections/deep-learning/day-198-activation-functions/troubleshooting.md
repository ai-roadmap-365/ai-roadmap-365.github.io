# Troubleshooting: Day 198 - Activation Functions

## Common Issues
1. **Floating Point Overflow in Exp:**
   - Cause: Exponentiating large positive numbers (> 709 in float64).
   - Fix: Use numerically stable formulations (e.g. subtract max(z) in Softmax).
