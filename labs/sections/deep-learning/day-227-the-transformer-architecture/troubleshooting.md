# Troubleshooting: Day 227 - The Transformer Architecture

## Common Issues
1. **Vanishing gradients in deep stacks:**
   - Cause: LayerNorm applied to residual sum instead of input branch (Post-LN).
   - Fix: Use Pre-LN `x = x + SubLayer(LayerNorm(x))`.
