# Troubleshooting: Day 204 - PyTorch: autograd and nn.Module

## Common Issues
1. **RuntimeError: Trying to backward through the graph a second time:**
   - Cause: Calling `loss.backward()` multiple times without `retain_graph=True`.
   - Fix: Only call `loss.backward()` once per training iteration.
