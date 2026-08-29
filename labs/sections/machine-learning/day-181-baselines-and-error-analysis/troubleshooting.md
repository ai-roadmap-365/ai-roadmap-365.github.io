# Troubleshooting Model Baselines & Error Analysis

## 1. Complex Model Fails to Beat Linear Baseline
If a 500-tree Gradient Booster achieves identical test score to Logistic Regression, your problem is linearly separable or features lack non-linear signal. Simplify architecture to reduce latency and maintenance costs.

## 2. Slices with Too Few Samples
Do not draw conclusions from slices with $N < 30$ samples. Use confidence intervals to evaluate slice error rates.
