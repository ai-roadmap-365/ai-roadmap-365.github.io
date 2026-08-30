# Security Considerations - Day 291
1. **Builtin Scoping:** Math execution is stripped of `__builtins__` to prevent arbitrary OS code execution.
2. **Context Bounding:** Sliding window memory bounds context growth, preventing memory exhaustion.
