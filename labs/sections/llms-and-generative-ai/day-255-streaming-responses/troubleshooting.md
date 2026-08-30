# Troubleshooting: Day 255 - Streaming Responses

## Common Issues
1. **Stdout buffering delay:**
   - Cause: print without flush=True.
   - Fix: Use sys.stdout.flush() or print(..., flush=True).
