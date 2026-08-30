# Troubleshooting: Day 262 - Vector Databases

## Common Issues
1. **Empty search results:**
   - Cause: Index has zero documents added before search.
   - Fix: Check len(self.vectors) > 0 before starting graph traversal.
