# Troubleshooting Guide for Day 174

## Common Issues

### 1. Complete Case Deletion (Listwise Deletion) Destroys 80% of Data
- **Symptom:** Running `df.dropna()` reduces a 100,000-row dataset to 15,000 rows.
- **Cause:** Discarding entire rows whenever any single feature is missing.
- **Fix:** Use conditional imputation (`SimpleImputer`, `KNNImputer`, or `IterativeImputer`) combined with `MissingIndicator`.

### 2. GBDT Crashing on Custom Missing Encodings (-999 vs NaN)
- **Symptom:** LightGBM treats `-999` as an extreme numerical value rather than missing data.
- **Cause:** Manually imputing missing entries with arbitrary magic numbers.
- **Fix:** Keep missing values as `np.nan` for LightGBM/XGBoost, allowing native default split routing.
