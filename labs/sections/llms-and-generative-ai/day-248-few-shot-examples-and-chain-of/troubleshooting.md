# Troubleshooting: Day 248 - Few-Shot Examples and Chain of Thought

## Common Issues
1. **Low reasoning diversity:**
   - Cause: Sampling with Temperature = 0 in Self-Consistency.
   - Fix: Use Temperature = 0.7 when sampling multiple CoT paths.
