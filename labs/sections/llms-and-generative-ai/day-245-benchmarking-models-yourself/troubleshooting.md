# Troubleshooting: Day 245 - Benchmarking Models Yourself

## Common Issues
1. **Pass@k index error:**
   - Cause: Looping $i$ beyond $k-1$.
   - Fix: Use `range(k)` to multiply exactly $k$ factor terms.
