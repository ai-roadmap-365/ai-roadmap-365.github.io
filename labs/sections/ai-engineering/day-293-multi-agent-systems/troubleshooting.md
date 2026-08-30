# Troubleshooting - Day 293
1. **Message Bus Filtering:** Use `get_messages_for(recipient)` to prevent message leakage between unrelated agents.
2. **Critic Rejection Loop:** Ensure the retry counter increments to avoid unbounded critique cycles.
