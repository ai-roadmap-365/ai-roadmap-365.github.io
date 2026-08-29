# Week 28 Project: Section Project -- Deployed ML Service

## Project Overview
Train, persist, register, serve, and monitor an enterprise-grade machine learning microservice:
1. **Model Pipeline:** Train a regularized customer churn classifier with stratified cross-validation and subgroup slice verification.
2. **Model Registry & Provenance:** Export weights with cryptographic SHA-256 hashing, semantic versioning (`v1.0.0`), and automated stage promotion (`PRODUCTION`).
3. **REST Serving API:** Host the model behind a low-latency FastAPI service with Pydantic request validation, batch endpoints, and automated circuit-breaker fallback heuristics.
4. **Production Observability:** Implement a real-time Population Stability Index (PSI) drift detector alerting on statistical feature distribution shifts.

## Business Context & Motivation
An enterprise subscription SaaS company processes 50,000 daily user account updates. When unvalidated models were previously deployed, silent data drift and API exceptions caused thousands of customer accounts to be incorrectly flagged for cancellation, eroding monthly recurring revenue (MRR).

This project delivers a bulletproof, fault-tolerant ML microservice ensuring 99.99% operational uptime and automated drift alerting.

---

## Architecture and Requirements

```
Raw Customer Ingestion -> Train & Validate -> SHA-256 Model Registry -> FastAPI Microservice -> PSI Drift Monitor
```

### 1. Training & Preprocessing Pipeline
- Train a regularized classification pipeline on customer behavioral features.
- Evaluate ROC-AUC and PR-AUC, asserting zero slice regression on key customer segments.

### 2. Model Registry & Provenance Catalog
- Compute SHA-256 hash of binary model weights.
- Store lineage metadata (Git commit SHA, training metrics, dataset hash).
- Enforce single-model `PRODUCTION` stage uniqueness.

### 3. FastAPI Microservice Serving
- Preload model artifact in memory on startup.
- Validate incoming requests with Pydantic schema boundaries.
- Implement `/predict` and `/predict_batch` endpoints.
- Wrap forward inference in a circuit-breaker fallback.

### 4. Real-Time Drift Observability
- Maintain quantile reference bins on training data.
- Compute Population Stability Index (PSI) on streaming production payloads.
- Trigger alerts when PSI >= 0.20 (Significant Drift).

---

## Free and open-source options
- Python 3.11+ with NumPy, pandas, scikit-learn, FastAPI, Pydantic, and pytest.
