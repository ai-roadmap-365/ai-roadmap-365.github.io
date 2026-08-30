# Troubleshooting: Day 264 - Hybrid Search and Re-Ranking

## Common Issues
1. **Division by zero during average doc length calculation:**
   - Cause: Empty document list indexed.
   - Fix: Use max(1, n_docs) in divisor.
