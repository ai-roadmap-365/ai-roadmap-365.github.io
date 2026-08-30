# Troubleshooting: Day 251 - Prompt Injection and Safe Prompting

## Common Issues
1. **Unescaped delimiter tags in payload:**
   - Cause: User text closing sandbox tags.
   - Fix: Escape closing tags before wrapping in XML.
