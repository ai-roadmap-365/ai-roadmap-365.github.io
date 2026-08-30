# Troubleshooting: Day 253 - First Calls to the Claude API

## Common Issues
1. **System prompt in messages error:**
   - Cause: Passing role="system" inside messages list.
   - Fix: Pass system as top-level system parameter.
