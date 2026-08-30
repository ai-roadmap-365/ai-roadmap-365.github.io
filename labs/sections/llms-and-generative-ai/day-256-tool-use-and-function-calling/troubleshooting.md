# Troubleshooting: Day 256 - Tool Use and Function Calling

## Common Issues
1. **Unregistered tool call error:**
   - Cause: Model requested a tool name not present in the dispatcher registry.
   - Fix: Ensure all declared tool schemas have corresponding registered Python functions.
