# Troubleshooting: Day 263 - Chunking Strategies

## Common Issues
1. **Empty chunks produced:**
   - Cause: Consecutive newlines or empty header sections.
   - Fix: Check text_content.strip() before appending to chunks list.
