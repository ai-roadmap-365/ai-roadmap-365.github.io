# Troubleshooting Metric Calculations

## 1. Zero Division in Precision / Recall
When no samples are predicted positive ($TP + FP = 0$), Precision is mathematically undefined. Guard division with an epsilon: `precision = tp / max(tp + fp, 1e-9)`.

## 2. Severe Class Imbalance Distorting ROC-AUC
When positives make up $< 1\%$ of the dataset, a high False Positive count can still produce a deceptive ROC-AUC of 0.98. Always use PR-AUC (Average Precision) alongside ROC-AUC for imbalanced distributions.
