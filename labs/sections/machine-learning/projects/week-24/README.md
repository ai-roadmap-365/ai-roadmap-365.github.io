# Week 24 Project: The Tabular Challenge — Linear vs Tuned Boosters vs Stacking

## Project Overview
Compete against your own baseline on a realistic tabular dataset (e.g. California Housing, Breast Cancer Diagnostic, or Synthetic Credit Default): build a rigorous, leak-free machine learning tournament comparing regularized Linear models against tuned Tree Ensembles (Random Forest, LightGBM, XGBoost) and a 2-Level Stacking Ensemble, documenting the exact progression of validation improvements.

## Business Context & Motivation
In enterprise tabular modeling, teams often jump straight to complex neural architectures or heavy ensemble stacks without establishing whether a simple linear model is already sufficient, or without quantifying the exact performance ROI of gradient boosting.

This project enforces the industry **Tabular Master Playbook**:
1. Anchor a leak-free Stratified 5-Fold Cross-Validation harness.
2. Establish a rock-solid Linear Baseline with standardized features.
3. Build and tune Gradient Boosted Decision Trees (LightGBM / XGBoost) with Bayesian hyperparameter optimization.
4. Construct a 2-Level Stacking Ensemble combining tree models and linear estimators.
5. Compute Permutation Feature Importance and TreeSHAP values for model explainability.
6. Produce an executive Model Comparison Audit Report comparing validation AUC, test AUC, training time, and inference latency.

---

## Architecture and Requirements

```
Raw Tabular Dataset
  └──> Leak-Free Stratified 5-Fold CV Split
        ├──> Benchmark 1: Standardized Logistic Regression / Ridge Baseline
        ├──> Benchmark 2: Tuned Random Forest Classifier (Subspace Bagging)
        ├──> Benchmark 3: Tuned LightGBM / XGBoost Booster (Histogram GOSS)
        ├──> Benchmark 4: 2-Level Stacking Ensemble (OOF Predictions -> Ridge Meta-Learner)
        └──> Explainability: Permutation Importance & TreeSHAP Attribution
```

### 1. Leak-Free Cross-Validation Anchor
- Partition data into an 80% Training split and a 20% untouched Holdout Test split.
- Inside the training split, implement Stratified 5-Fold Cross-Validation.
- Wrap all feature scaling and imputation inside a scikit-learn `Pipeline` to eliminate preprocessing leakage.

### 2. The 4-Way Model Tournament
Train and evaluate the following 4 model architectures across the 5 folds:
1. **Linear Baseline:** `Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression(C=1.0))])`.
2. **Random Forest:** `RandomForestClassifier(n_estimators=100, max_depth=6, max_features='sqrt')`.
3. **Tuned Gradient Booster:** `GradientBoostingClassifier` (or `LGBMClassifier`) tuned via Randomized Search / Optuna on `learning_rate`, `max_depth`, `subsample`, and `n_estimators`.
4. **Stacking Ensemble:** A 2-level stack taking out-of-fold probability predictions from Models 1, 2, and 3 and passing them to a `LogisticRegression(C=1.0)` meta-learner.

### 3. Model Explainability Audit
- Compute Permutation Feature Importance on the holdout test set to identify the top 5 predictive features.
- Analyze feature interactions and verify that no single uninformative noise feature received high importance.

### 4. Executive Model Comparison Matrix
Produce a Markdown audit table documenting:
- Mean 5-Fold Cross-Validation ROC-AUC (+/- standard deviation).
- Final Holdout Test ROC-AUC and F1-Score.
- Total Training Wall-Clock Time (seconds).
- Single-Sample Inference Latency (milliseconds).

---

## Expected output

A complete run of the Tabular Challenge pipeline prints the tournament leaderboard and executive comparison:

```text
================================================================================
WEEK 24 PROJECT: TABULAR CHALLENGE TOURNAMENT LEADERBOARD
================================================================================
Dataset: Breast Cancer Wisconsin Diagnostic (n=569 samples, d=30 features)
Splits: Training=455 (80%), Holdout Test=114 (20%)
Validation Scheme: Stratified 5-Fold Cross-Validation

--- 1. Model Tournament Results (5-Fold CV on Training Split) ---
• Model 1 [Logistic Regression]:   CV ROC-AUC = 0.9882 (+/- 0.0091) | Train Time: 0.012s
• Model 2 [Random Forest]:         CV ROC-AUC = 0.9904 (+/- 0.0062) | Train Time: 0.145s
• Model 3 [Tuned Gradient Boost]:  CV ROC-AUC = 0.9938 (+/- 0.0041) | Train Time: 0.220s
• Model 4 [2-Level Stacking]:      CV ROC-AUC = 0.9965 (+/- 0.0032) | Train Time: 0.410s  [CHAMPION]

--- 2. Final Holdout Test Set Sign-Off (114 samples) ---
Model                              Test Accuracy  Test ROC-AUC   Test F1-Score  Inference Latency
--------------------------------------------------------------------------------------------------
1. Logistic Regression (Baseline)  95.61%         0.9854         0.9655         0.02 ms/sample
2. Random Forest                   96.49%         0.9892         0.9722         0.15 ms/sample
3. Tuned Gradient Boosting         97.37%         0.9941         0.9793         0.08 ms/sample
4. 2-Level Stacking Ensemble       98.25%         0.9972         0.9861         0.25 ms/sample

--- 3. Top 5 Most Predictive Features (Permutation Importance) ---
1. worst concave points     : Mean Accuracy Drop = 4.39% (+/- 0.88%)
2. worst perimeter          : Mean Accuracy Drop = 3.51% (+/- 0.75%)
3. worst radius             : Mean Accuracy Drop = 2.63% (+/- 0.62%)
4. mean concave points      : Mean Accuracy Drop = 1.75% (+/- 0.45%)
5. mean texture             : Mean Accuracy Drop = 1.20% (+/- 0.30%)
================================================================================
STATUS: TOURNAMENT COMPLETED — STACKING DELIVERS +1.18% ROC-AUC OVER BASELINE
================================================================================
```

---

## Validation

Execute the full project validation pipeline to verify your implementation:

```bash
# 1. Activate environment
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scikit-learn pytest scipy

# 2. Run the Tabular Challenge pipeline
python3 tabular_challenge_project.py

# 3. Verify all test assertions
pytest tests/ -v
```

### Self-Check Verification Checklist
1. **Zero Preprocessing Leakage:** Ensure scalers and imputers are strictly fitted on training splits inside cross-validation loops.
2. **Out-of-Fold Invariant:** Ensure Level-1 meta-features `Z` are generated strictly out-of-fold across the 5 splits.
3. **Single Test Evaluation:** Holdout test set must be evaluated strictly once after all model selection and ensembling is finalized.
