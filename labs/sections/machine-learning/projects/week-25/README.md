# Week 25 Project: The Feature Engineering Challenge — Improving Fixed Models Through Representation

## Project Overview
Improve a fixed, frozen baseline model's predictive performance **purely through feature engineering and data representation** on a complex, un-sanitized tabular dataset: apply domain transformations, cyclical time encodings, polynomial interactions, out-of-fold smoothed target encodings, missingness flags, and feature selection inside atomic scikit-learn Pipelines, documenting the exact marginal impact of each feature iteration.

## Business Context & Motivation
In production machine learning systems, deploying a complex new neural network or heavy ensemble often violates strict latency budgets, increases cloud inference costs, or fails regulatory explainability compliance.

Engineers are frequently constrained: **the model architecture is fixed (e.g. a simple Logistic Regression or Ridge model for sub-millisecond inference and linear compliance)**.

The only lever available to improve business metrics is **Feature Engineering**.

This project enforces the end-to-end Week 25 Feature Mastery Workflow:
1. Establish a frozen baseline model on raw un-engineered features.
2. Formulate and inject domain ratios, physics interactions, and non-linear transformations.
3. Apply 2D trigonometric cyclical encoding on periodic temporal variables.
4. Construct leak-free Out-of-Fold Smoothed Target Encoding for high-cardinality nominal variables.
5. Engineer explicit `MissingIndicator` flags and conditional imputation.
6. Prune uninformative noise using Boruta or RFECV feature selection.
7. Encapsulate everything in a production-ready scikit-learn `Pipeline` and `ColumnTransformer`.
8. Produce an executive Feature Ablation Audit tracking the exact progression of validation gains.

---

## Architecture and Requirements

```
Raw Un-Sanitized Tabular Dataset
  ├──> Continuous Skewed Features ➔ RobustScaler / Yeo-Johnson Power Transform
  ├──> Periodic Timestamp Features ➔ 2D Trigonometric (sin, cos) Unit Circle Coordinates
  ├──> High-Cardinality Nominal ➔ Out-of-Fold Smoothed Target Encoding (m=10)
  ├──> Multi-Attribute Physics ➔ Domain Ratios (Debt-to-Income, BMI, Price-per-SqFt)
  ├──> Missing Value Signals ➔ SimpleImputer(median) + MissingIndicator(flags)
  └──> Feature Selection Funnel ➔ VarianceThreshold ➔ Boruta / RFECV (Top K Pruning)
        └──> Frozen Fixed Estimator (Ridge / LogisticRegression) ➔ Production Serving
```

### 1. The Frozen Estimator Constraint
- Model: A simple, fixed linear estimator (e.g. `Ridge(alpha=1.0)` or `LogisticRegression(C=1.0, solver='lbfgs')`).
- **Rule:** You are strictly forbidden from changing the model algorithm or tuning model hyperparameters. All performance gains must originate 100% from feature engineering!

### 2. Feature Engineering Iterations (5 Progressive Stages)
Document the metric progression (e.g. $R^2$ or ROC-AUC) across 5 sequential engineering stages:
- **Stage 0 (Baseline):** Raw numerical and one-hot encoded features with simple mean imputation.
- **Stage 1 (Scaling & Imputation):** Outlier-resistant `RobustScaler` + `SimpleImputer(median, add_indicator=True)`.
- **Stage 2 (Domain Ratios & Interactions):** Multiplicative interactions $x_i \cdot x_j$ and domain-specific quotients.
- **Stage 3 (Temporal & Categorical Encodings):** 2D Cyclical $(\sin, \cos)$ coordinates + leak-free OOF Target Encoding.
- **Stage 4 (Feature Selection):** Pruning noisy and redundant columns via `VarianceThreshold` and `RFE` / `Boruta`.

### 3. Strict Prevention of Data Leakage
- All scalers, imputers, target encodings, and feature selectors **must be encapsulated inside a scikit-learn `Pipeline` and `ColumnTransformer`**.
- Cross-validation must be executed using 5-Fold Stratified K-Fold.

### 4. Executive Feature Progression Report
Produce a markdown report table detailing:
- Stage Name and Description of added features.
- Total Feature Count ($D$).
- 5-Fold Cross-Validation Score ($\pm 	ext{std}$).
- Holdout Test Score.
- Marginal Metric Delta ($\Delta 	ext{Score}$).

---

## Free and open-source options
- Python 3.11+ with NumPy, SciPy, scikit-learn, and pytest (all free, open source).

## Installation
```bash
python3 -m venv .venv
.venv/bin/pip install -r ../../day-175-features-beat-algorithms/requirements/requirements.txt
```

## Expected output

A complete run of the challenge pipeline prints the progression leaderboard:

```text
================================================================================
WEEK 25 FEATURE ENGINEERING CHALLENGE: FROZEN MODEL TOURNAMENT
Fixed Model: Ridge Regression (alpha=1.0)
Dataset: Synthetic Multi-Modal Tabular Benchmark (n=1000, 5-Fold CV)
================================================================================
Stage 0 (Raw Baseline):                   5-Fold CV R2 = 0.3842 +/- 0.0310 | Test R2 = 0.3791 (d=5)
Stage 1 (RobustScaler + MissingFlags):    5-Fold CV R2 = 0.5420 +/- 0.0245 | Test R2 = 0.5388 (d=8)  [+15.97%]
Stage 2 (Domain Ratios & Products):       5-Fold CV R2 = 0.7814 +/- 0.0182 | Test R2 = 0.7795 (d=14) [+24.07%]
Stage 3 (Cyclical Time + OOF Target):     5-Fold CV R2 = 0.9412 +/- 0.0094 | Test R2 = 0.9380 (d=18) [+15.85%]
Stage 4 (Boruta / RFE Feature Selection): 5-Fold CV R2 = 0.9845 +/- 0.0041 | Test R2 = 0.9822 (d=12) [+04.42%]
================================================================================
TOTAL FEATURE ENGINEERING GAIN: +0.6031 R2 (+159.1% Relative Improvement!)
Inference Latency: 0.09 milliseconds (Ultra-low production latency preserved!)
================================================================================
```

---

## Validation

Execute the full project validation pipeline to verify your implementation:

```bash
# 1. Activate environment
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scikit-learn pytest scipy pandas

# 2. Run the Feature Engineering Challenge pipeline
python3 feature_engineering_challenge.py

# 3. Verify all test assertions
pytest tests/ -v
```

### Self-Check Verification Checklist
1. **Zero Preprocessing Leakage:** Ensure all domain transformations, scalers, imputers, and target encodings are fitted strictly on training folds inside cross-validation loops.
2. **Fixed Model Invariant:** Ensure the model architecture (`Ridge(alpha=1.0)`) remains strictly frozen and unchanged across all 5 stages.
3. **Single Test Evaluation:** Holdout test set must be evaluated strictly once after all feature engineering and selection is finalized.

---

## Submission Checklist
- [ ] Complete Python script implementing all 5 feature engineering stages.
- [ ] Leak-free ColumnTransformer and Pipeline architecture.
- [ ] Out-of-fold smoothed target encoding without data leakage.
- [ ] 2D trigonometric cyclical time encoding.
- [ ] Markdown executive feature progression audit report.
