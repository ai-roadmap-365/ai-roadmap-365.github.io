# Troubleshooting Guide for Day 159

## Common Issues

### 1. Division by Zero in Precision or Recall
- **Symptom:** `ZeroDivisionError` or `RuntimeWarning: invalid value encountered in scalar divide` when `TP + FP == 0` (e.g. threshold is so high that no positives are predicted).
- **Cause:** No positive predictions made.
- **Fix:** Guard against zero denominators: `precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0`.

### 2. Misleading ROC Curves on Heavily Imbalanced Data
- **Symptom:** ROC AUC is 0.98, but the model has virtually zero precision in practice.
- **Cause:** Large numbers of True Negatives suppress the False Positive Rate `FPR = FP / (TN + FP)`, making ROC look artificially optimistic.
- **Fix:** Use the Precision-Recall (PR) curve and Average Precision (PR AUC) when positive class prevalence is low (<5%).
