# Troubleshooting: Day 212 - CNN Architectures

## Common Issues
1. **Shape mismatch at `out += residual`:**
   - Cause: Input tensor channels do not match output channels.
   - Fix: Use a 1x1 conv projection in the shortcut path.
