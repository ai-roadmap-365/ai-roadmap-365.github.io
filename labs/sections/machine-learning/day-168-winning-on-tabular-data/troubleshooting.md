# Troubleshooting Guide for Day 168

## Common Issues

### 1. Target Overfitting in Stacking Meta-Learner
- **Symptom:** Stacking ensemble scores 99% on training folds but performs worse than single base models on test data.
- **Cause:** Generating Level-1 meta-features `Z` using standard training predictions (`model.fit(X).predict(X)`) rather than leak-free out-of-fold cross-validation predictions.
- **Fix:** Always generate `Z` using strict out-of-fold cross-validation (`generate_out_of_fold_predictions`).

### 2. High Correlation Between Level-0 Base Models
- **Symptom:** Stacking three identical Random Forests yields zero performance gain over a single model.
- **Cause:** Ensembling requires model diversity (e.g. combining LightGBM + XGBoost + CatBoost + Logistic Regression + Neural Tabular).
- **Fix:** Mix structurally diverse model families with different inductive biases.
