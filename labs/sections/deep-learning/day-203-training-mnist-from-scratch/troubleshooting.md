# Troubleshooting: Day 203 - Training MNIST from Scratch

## Common Issues
1. **Low Accuracy on MNIST:**
   - Cause: Untuned learning rate or missing He initialization.
   - Fix: Use learning rate 0.1 with momentum 0.9 and He initialization.
