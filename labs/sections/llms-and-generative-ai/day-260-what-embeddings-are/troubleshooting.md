# Troubleshooting: Day 260 - What Embeddings Are

## Common Issues
1. **Cosine similarity out of range [-1, 1]:**
   - Cause: Numerical floating-point roundoff error in dot products.
   - Fix: Use np.clip(sim, -1.0, 1.0) before downstream arcsin/arccos calculations.
