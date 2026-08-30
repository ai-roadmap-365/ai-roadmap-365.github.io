# Troubleshooting: Day 216 - Beyond Classification

## Common Issues
1. **Division by zero in IoU:**
   - Cause: Both boxes have zero area.
   - Fix: Return 0.0 if `union_area == 0.0`.
