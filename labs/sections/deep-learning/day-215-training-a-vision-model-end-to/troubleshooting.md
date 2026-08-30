# Troubleshooting: Day 215 - Training a Vision Model End to End

## Common Issues
1. **Memory leak during validation:**
   - Cause: Computing metrics without `torch.no_grad()`.
   - Fix: Always wrap evaluation loops in `with torch.no_grad():`.
