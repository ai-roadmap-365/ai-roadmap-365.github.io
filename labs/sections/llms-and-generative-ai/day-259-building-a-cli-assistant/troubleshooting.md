# Troubleshooting: Day 259 - Building a CLI Assistant

## Common Issues
1. **System prompt missing after turn eviction:**
   - Cause: Putting system prompt inside the sliding deque.
   - Fix: Prepend the immutable system prompt explicitly in build_message_context.
