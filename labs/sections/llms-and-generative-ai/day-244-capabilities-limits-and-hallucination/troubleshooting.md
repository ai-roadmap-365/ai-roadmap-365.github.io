# Troubleshooting: Day 244 - Capabilities, Limits, and Hallucination

## Common Issues
1. **Regex number parsing failure:**
   - Cause: Splitting floating point numbers at decimal points.
   - Fix: Use `r'\b\d+(?:\.\d+)?\b'` to capture whole floats.
