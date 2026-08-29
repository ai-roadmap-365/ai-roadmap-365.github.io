# Troubleshooting: Day 201 - A Neural Network in Pure NumPy

## Common Issues
1. **Network Fails to Learn Non-Linear Boundary:**
   - Cause: Insufficient hidden neurons or learning rate too small.
   - Fix: Use at least 16 hidden units in layer 1 and set learning rate to 0.05-0.1.
