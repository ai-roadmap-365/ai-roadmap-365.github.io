# Week 26 Project: Model Audit Report — End-to-End Evaluation, Fairness, and Governance

## Project Overview
Execute a comprehensive, end-to-end audit on a trained machine learning model slated for high-stakes enterprise deployment: systematically detect and eliminate data leakage, evaluate algorithmic fairness across demographic subgroups (Demographic Parity, Disparate Impact, Equal Opportunity), conduct slice-based error analysis with Andrew Ng's error reduction ceilings, generate game-theoretic SHAP feature attributions, and compile an executive, decision-ready Model Card conforming to the Mitchell et al. (2019) and EU AI Act Article 11 standards.

## Business Context & Motivation
An enterprise bank or clinical healthcare provider is preparing to deploy an automated risk assessment model. The model scores a high validation metric (e.g. 0.94 ROC-AUC), but executive leadership and compliance officers require a formal, independent **Model Audit** before deployment approval.

Deploying an un-audited machine learning model risks:
1. **Catastrophic Production Failure** due to hidden target leakage or patient group contamination.
2. **Multi-Million-Dollar Regulatory Fines & Lawsuits** under the Equal Credit Opportunity Act (ECOA), EEOC Title VII, or EU AI Act for unmonitored disparate impact.
3. **Severe Localized Blind Spots** where the model fails on 40% of high-value enterprise accounts despite high global accuracy.

This project synthesizes the complete Week 26 Evaluation & Interpretation curriculum into a production-grade audit pipeline.

---

## Architecture and Requirements

```
Trained Model & Pre-Deployment Dataset
  ├──> 1. Data Leakage Audit ➔ Target Correlations, Group Overlap, Preprocessing Integrity
  ├──> 2. Algorithmic Fairness Audit ➔ Disparate Impact (80% Rule), Equal Opportunity, Predictive Parity
  ├──> 3. Systematic Error Analysis ➔ Subgroup Slicing & Andrew Ng Error Reduction Ceilings
  ├──> 4. Interpretability Suite ➔ Global Permutation MDA & Game-Theoretic SHAP Attributions
  └──> 5. Governance Synthesis ➔ 9-Section Mitchell et al. (2019) Enterprise Model Card
```

### 1. Data Leakage & Pipeline Integrity Audit
- Inspect feature schemas for target proxies, temporal lookahead bias, and train/test group contamination.
- Enforce strict `GroupKFold` or `TimeSeriesSplit` cross-validation encapsulation.

### 2. Multi-Metric Algorithmic Fairness Audit
- Quantify selection rates across demographic protected groups $A \in \{0, 1\}$.
- Compute the **Disparate Impact Ratio** against the EEOC 4/5ths ($0.80$) threshold.
- Compute the **Equal Opportunity Difference** (True Positive Rate delta).
- Document trade-offs dictated by the **Impossibility Theorem of Algorithmic Fairness**.

### 3. Systematic Error & Slice Analysis
- Extract 100+ misclassified validation instances.
- Categorize errors into a structured taxonomy (e.g. Label Noise, Feature Missingness, Subclass Outliers).
- Calculate the **Error Reduction Ceiling** for each category: $\Delta \text{Accuracy}_{\text{max}} = \frac{E_{\text{cat}}}{N_{\text{val}}}$.
- Produce slice performance tables across operational and demographic attributes.

### 4. Game-Theoretic Interpretability Suite
- Compare biased Tree Gini MDI against out-of-sample **Permutation Feature Importance**.
- Compute game-theoretic **Shapley Values** satisfying the 4 core axioms (Efficiency, Symmetry, Dummy Player, Additivity).
- Generate local waterfall explanations and global summary attributions.

### 5. Enterprise Model Card Compilation
- Author the complete 9-section Model Card in Markdown conforming to Mitchell et al. (2019):
  1. Model Details & Versioning
  2. Intended Use & **Mandatory Out-of-Scope Declarations**
  3. Factors & Demographic Slices
  4. Metrics & Multi-Tier Baseline Comparisons (Dummy, Domain Rule, Linear)
  5. Evaluation Data & Split Integrity
  6. Training Data & Feature Lineage
  7. Quantitative Analyses & Subgroup Slices
  8. Ethical Considerations & Risk Mitigations
  9. Caveats, Operational Limits, and Retraining Triggers

---

## Free and open-source options
- Python 3.11+ with NumPy, pandas, SciPy, scikit-learn, and pytest (all free, open source).

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy pandas scipy scikit-learn pytest
```

## Expected output

Executing the Model Audit suite produces a comprehensive compliance evaluation:

```text
================================================================================
WEEK 26 PROJECT: ENTERPRISE MODEL AUDIT & COMPLIANCE REPORT
Model: ClinicalSepsisClassifier-v2.1.0 (LightGBM Ensemble)
================================================================================
1. DATA LEAKAGE AUDIT:
   - Target Leakage Check:       PASS (Max feature-target correlation: 0.412)
   - Preprocessing Isolation:    PASS (Encapsulated in scikit-learn Pipeline)
   - Group Overlap Audit:        PASS (0 / 1000 overlapping patient IDs)

2. ALGORITHMIC FAIRNESS SCORECARD:
   - Group 0 (Unprivileged) Selection Rate: 0.1850
   - Group 1 (Privileged) Selection Rate:   0.2100
   - Disparate Impact Ratio:                0.8810 (PASS >= 0.80 EEOC Threshold)
   - Equal Opportunity Difference (TPR):    0.0240 (PASS <= 0.05 Target)

3. ERROR & SLICE ANALYSIS:
   - Baseline Hierarchy: Beats Dummy (+38.2%) and Domain Rule (+12.4%)
   - Slice Audit: Age < 50 (PR-AUC 0.86) vs Age >= 50 (PR-AUC 0.84)
   - Top Error Ceiling: Label Noise (+3.2% max achievable accuracy gain)

4. INTERPRETABILITY & SHAP:
   - Top Global Drivers: Blood Pressure, Lactate Level, Respiration Rate
   - Shapley Efficiency Axiom: Verified (Residual = 0.00e+00)

5. GOVERNANCE STATUS:
   - 9-Section Model Card: COMPILED & VALIDATED
   - Regulatory Compliance: READY FOR DEPLOYMENT SIGN-OFF
================================================================================
```

---

## Validation

Execute the project verification script to validate your implementation:

```bash
# 1. Run the Model Audit pipeline
python3 model_audit_pipeline.py

# 2. Verify all test assertions
pytest tests/ -v
```

### Self-Check Verification Checklist
1. **Zero Leakage:** Confirm that no test patient IDs exist in training splits.
2. **EEOC Compliance:** Confirm Disparate Impact Ratio $\ge 0.80$.
3. **Model Card Schema:** Ensure all 9 Mitchell sections are present and non-empty.
4. **Out-of-Scope Section:** Ensure prohibited use cases are explicitly defined.

---

## Submission Checklist
- [ ] Automated Data Leakage detection module.
- [ ] Subgroup Fairness and Disparate Impact evaluation module.
- [ ] Error Analysis and Slice Breakdown script with Andrew Ng Ceilings.
- [ ] Permutation and SHAP interpretability module.
- [ ] Complete, validated `MODEL_CARD.md` document.
