# Troubleshooting: Day 240 - Pretraining, Fine-Tuning, and RLHF

## Common Issues
1. **DPO Loss divergence:**
   - Cause: $eta$ parameter set too high ($> 1.0$).
   - Fix: Keep $eta$ in range $[0.05, 0.20]$.
