# Troubleshooting Data Leakage

## 1. Suspiciously High ROC-AUC (> 0.99)
If a complex real-world tabular dataset yields ROC-AUC $> 0.99$ on the very first training run, assume data leakage until proven otherwise. Inspect top SHAP features for metadata or target proxies.

## 2. Inconsistent Splitters
Ensure time series data uses `TimeSeriesSplit` and grouped patient data uses `GroupKFold` or `StratifiedGroupKFold`.
