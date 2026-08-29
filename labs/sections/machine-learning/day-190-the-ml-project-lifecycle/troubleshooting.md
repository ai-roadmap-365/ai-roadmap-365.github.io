# Troubleshooting: Day 190 - The ML Project Lifecycle

## Common Issues
1. **Unchecked Subgroups:**
   - Cause: Missing slice dictionary entries.
   - Fix: Use `.get(key, 0.0)` with fallback.
