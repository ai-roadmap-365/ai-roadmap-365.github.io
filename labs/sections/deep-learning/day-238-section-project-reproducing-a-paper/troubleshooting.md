# Troubleshooting: Day 238 - Section Project: Reproducing a Paper

## Common Issues
1. **Single batch overfit divergence:**
   - Cause: LayerNorm applied incorrectly across sequence dimension instead of embedding dimension.
   - Fix: Use `nn.LayerNorm(embed_dim)`.
