# Troubleshooting: Day 266 - End-to-End RAG System

## Common Issues
1. **Low confidence on exact matches:**
   - Cause: Query words split differences.
   - Fix: Lowercase and strip punctuation before computing word overlap.
