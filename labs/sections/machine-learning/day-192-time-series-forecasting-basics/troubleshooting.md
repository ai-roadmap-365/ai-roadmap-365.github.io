# Troubleshooting: Day 192 - Time Series Forecasting Basics

## Common Issues
1. **Lookahead Data Leakage:**
   - Cause: Rolling window includes current index `t`.
   - Fix: Use slice `[t - window_size : t]`.
