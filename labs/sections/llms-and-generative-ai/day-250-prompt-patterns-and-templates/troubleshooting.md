# Troubleshooting: Day 250 - Prompt Patterns and Templates

## Common Issues
1. **Missing Jinja2 template partial:**
   - Cause: Relative path misconfiguration in include statement.
   - Fix: Configure Jinja2 FileSystemLoader with absolute template directory.
