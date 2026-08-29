# Troubleshooting: Day 210 - A Disciplined Training Project

## Common Issues
1. **Checkpoint corrupted on power loss:**
   - Cause: Writing directly to target file.
   - Fix: Write to a `.tmp` file first and use `os.replace` for atomic updates.
