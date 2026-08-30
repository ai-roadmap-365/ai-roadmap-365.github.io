# Troubleshooting: Day 213 - Transfer Learning

## Common Issues
1. **Backbone weights changing when frozen:**
   - Cause: Passing frozen parameters to the optimizer without checking `p.requires_grad`.
   - Fix: Filter optimizer parameters: `[p for p in model.parameters() if p.requires_grad]`.
