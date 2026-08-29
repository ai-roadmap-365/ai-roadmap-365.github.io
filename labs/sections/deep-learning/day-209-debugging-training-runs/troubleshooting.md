# Troubleshooting: Day 209 - Debugging Training Runs

## Common Issues
1. **Loss explodes to NaN:**
   - Cause: High learning rate or taking logarithm of 0.
   - Fix: Use `torch.autograd.set_detect_anomaly(True)` and apply `clip_grad_norm_`.
