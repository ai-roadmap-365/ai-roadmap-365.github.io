# Troubleshooting: Day 235 - Experiment Tracking

## Common Issues
1. **Corrupt JSONL records:**
   - Cause: Writing un-serialized objects to file.
   - Fix: Use `json.dumps()` on primitive Python dictionaries.
