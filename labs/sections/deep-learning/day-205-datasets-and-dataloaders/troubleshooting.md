# Troubleshooting: Day 205 - Datasets and DataLoaders

## Common Issues
1. **RuntimeError: stack expects each tensor to be equal size:**
   - Cause: Using default collate on variable length sequences.
   - Fix: Pass a custom `collate_fn` that pads sequences dynamically.
