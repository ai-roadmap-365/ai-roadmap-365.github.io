# Troubleshooting: Day 270 - Citations and Grounded Answers

## Common Issues
1. **Zero scores on BM25:**
   - Cause: Query tokens do not match document tokens.
   - Fix: Normalize text using regex word extraction and lowercasing.
