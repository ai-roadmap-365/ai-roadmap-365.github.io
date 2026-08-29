# Week 27 Project: Customer Segmentation & Behavioral Archetyping

## Project Overview
Design, build, evaluate, and deploy an enterprise-grade, end-to-end **Customer Segmentation Pipeline**: extract multi-dimensional behavioral features (Recency, Frequency, Monetary value) from transactional data lakes, remediate heavy right-skewed revenue distributions via power transformations, perform linear and non-linear dimensionality reduction (PCA and UMAP), execute K-Means and DBSCAN clustering with Silhouette and Davies-Bouldin optimization, isolate spending anomalies with Isolation Forests, and synthesize quantitative cluster centroids into executive-level CRM personas and automated marketing playbooks.

## Business Context & Motivation
An enterprise e-commerce platform processing millions of annual transactions treats all 500,000 active shoppers with a uniform email blast strategy. The results are severe:
1. **Margin Erosion:** 20% discount promotions are sent to loyal VIP shoppers who would have purchased at full price.
2. **Customer Churn:** Previously high-frequency shoppers who are slipping into dormancy receive generic newsletters rather than urgent win-back incentives.
3. **Wasted Marketing Budget:** Tens of thousands of dollars are spent retargeting lost, one-time shoppers with near-zero expected lifetime value.

To maximize customer lifetime value (LTV) and marketing ROI, the growth engineering team requires an automated unsupervised machine learning segmentation engine.

---

## Architecture and Requirements

```
Raw Transactional Invoices
  ├──> 1. RFM & Behavioral Feature Engineering (Snapshot aggregation, tenure, basket size)
  ├──> 2. Distribution Remediation & Preprocessing (Log1p power transform + StandardScaler)
  ├──> 3. Anomaly Isolation (Isolation Forest outlier detection & sanitization)
  ├──> 4. Dimensionality Reduction (PCA 90% variance threshold + UMAP 2D manifold embedding)
  ├──> 5. Multi-Model Clustering (K-Means++ vs Agglomerative vs DBSCAN)
  ├──> 6. Cluster Validation & Stability (Silhouette Analysis, Davies-Bouldin, Calinski-Harabasz)
  └──> 7. Persona Synthesis & Actionable Playbook (Champions, Loyalists, At-Risk, Dormant)
```

### 1. RFM & Feature Engineering Suite
- Compute **Recency ($R$)**: Days since last transaction relative to snapshot date.
- Compute **Frequency ($F$)**: Total count of unique completed orders.
- Compute **Monetary Value ($M$)**: Total gross customer spend.
- Compute **Average Order Value (AOV)** and **Customer Lifespan Tenure**.

### 2. Preprocessing & Outlier Screening
- Apply `np.log1p` transformation to compress exponential right-skewed revenue and order counts.
- Standardize all features to zero mean and unit variance using `StandardScaler`.
- Train an `IsolationForest` (contamination=0.02) to detect and separate extreme transaction anomalies.

### 3. Dimensionality Reduction & Visualization
- Apply **PCA** to find the optimal number of principal components capturing $\ge 90\%$ total variance.
- Generate a 2D **UMAP** manifold embedding to visualize local and global cluster topography.

### 4. Clustering & Optimal K Selection
- Fit `KMeans` across $k \in [2, 10]$.
- Plot **Elbow Curve (Inertia)** and compute **Silhouette Scores**, **Davies-Bouldin Index**, and **Calinski-Harabasz Index**.
- Benchmark against Hierarchical Agglomerative Clustering (Ward linkage) and DBSCAN.

### 5. Business Persona Generation & Strategy Document
- Translate quantitative centroid statistics into 4 core business archetypes:
  1. **👑 Champions:** Low Recency, High Frequency, High Spend.
  2. **💎 Loyalists:** Moderate Recency, High Frequency, Moderate Spend.
  3. **⚠️ At Risk:** High Recency, High Historic Spend, Moderate Past Frequency.
  4. **💤 Lost Dormant:** High Recency, Single Order, Low Spend.
- Author an executive strategy table detailing tailored CRM intervention triggers, coupon values, and email cadences for each segment.

---

## Free and open-source options
- Python 3.11+ with NumPy, pandas, SciPy, scikit-learn, and pytest.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy pandas scipy scikit-learn pytest
```

## Expected output

```text
================================================================================
WEEK 27 PROJECT: ENTERPRISE CUSTOMER SEGMENTATION ENGINE
Dataset: 50,000 Transactions | 10,000 Unique Customers
================================================================================
1. FEATURE ENGINEERING & PREPROCESSING:
   - RFM Aggregation: Completed (Shape: 10,000 x 5)
   - Log1p & StandardScaler: Applied (Mean: 0.00, Std: 1.00)
   - Isolation Forest: 200 Anomalies isolated (Contamination = 2.0%)

2. DIMENSIONALITY REDUCTION:
   - PCA Components Retained: 2 (Explained Variance: 92.4%)
   - UMAP Projection: Completed (Preserved manifold topology)

3. CLUSTERING OPTIMIZATION:
   - Evaluated k in range [2, 8]
   - Optimal k = 4 (Silhouette Score: 0.482 | Davies-Bouldin: 0.741)
   - Segment Distribution:
     * Cluster 0 (Champions):  1,450 users (14.8%) | Median Spend: $4,850
     * Cluster 1 (Loyalists):  3,100 users (31.6%) | Median Spend: $1,250
     * Cluster 2 (At-Risk):    2,450 users (25.0%) | Median Spend: $980
     * Cluster 3 (Dormant):    2,800 users (28.6%) | Median Spend: $45

4. BUSINESS PERSONAS & AUTOMATION PLAYBOOK:
   - Generated CRM Action Rules for 4 Archetypes
   - Executive Strategy Document compiled to CSV & Markdown
================================================================================
```

---

## Validation

Execute the project verification script to validate your segmentation engine:

```bash
# 1. Run the Customer Segmentation pipeline
python3 customer_segmentation_pipeline.py

# 2. Verify all test assertions
pytest tests/ -v
```

### Self-Check Verification Checklist
1. **Skewness Handled:** Verify that features have been log-transformed before K-Means clustering.
2. **Optimal K Justified:** Ensure Silhouette scores and Elbow curves are logged and evaluated.
3. **Actionable Personas:** Verify that each cluster is mapped to a concrete CRM intervention strategy.

---

## Submission Checklist
- [ ] Automated RFM feature engineering and snapshot aggregation module.
- [ ] Preprocessing and Isolation Forest outlier screening script.
- [ ] PCA and UMAP dimensionality reduction module.
- [ ] K-Means clustering optimization and evaluation suite (Silhouette & DB index).
- [ ] Complete executive persona strategy report.
