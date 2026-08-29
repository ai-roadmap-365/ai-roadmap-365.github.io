# Troubleshooting: Day 206 - Optimizers: SGD to Adam

## Common Issues
1. **RuntimeError: a leaf Variable that requires grad is being used in an in-place operation:**
   - Cause: Modifying parameters directly without `@torch.no_grad()`.
   - Fix: Ensure the `step()` method is decorated with `@torch.no_grad()`.
