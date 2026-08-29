# Troubleshooting: Day 207 - Learning Rate Schedules

## Common Issues
1. **UserWarning: Detected call of `lr_scheduler.step()` before `optimizer.step()`:**
   - Cause: Calling `scheduler.step()` before `optimizer.step()`.
   - Fix: Ensure `scheduler.step()` is called after `optimizer.step()`.
