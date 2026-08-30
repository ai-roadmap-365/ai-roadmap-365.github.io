# Troubleshooting: Day 231 - Fine-Tuning a Small Transformer

## Common Issues
1. **Weight decay applied to LayerNorm:**
   - Cause: Parameter name filter missed `LayerNorm.weight`.
   - Fix: Include `LayerNorm.weight` in `no_decay` list.
