# Security Considerations for Metric Evaluation

## 1. Metric Gaming and Goodhart's Law
When optimizing metrics like Accuracy or F1 in production, agents can exploit thresholds to artificially boost scores while degrading business utility. Always bind threshold optimization to explicit cost/utility matrices.

## 2. Leakage and Evaluation Boundaries
Ensure test labels are strictly isolated from metric calculation and threshold tuning. Tuning thresholds on test sets creates evaluation leakage.
