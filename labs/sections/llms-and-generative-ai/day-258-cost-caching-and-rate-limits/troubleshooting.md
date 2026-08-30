# Troubleshooting: Day 258 - Cost, Caching, and Rate Limits

## Common Issues
1. **Token rate limit overage:**
   - Cause: Sending large unthrottled burst requests.
   - Fix: Wrap request dispatchers in TokenBucket rate limit checks.
