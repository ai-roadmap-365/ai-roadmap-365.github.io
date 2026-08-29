# Week 23 Project: High-Precision Spam Classification Engine

## Project Overview
Build a production-grade, cost-sensitive email and SMS spam detection system capable of processing raw, messy text streams, extracting n-gram and TF-IDF feature representations, benchmarking generative (Multinomial Naive Bayes) against discriminative (Logistic Regression) classifiers, and tuning decision thresholds under severe asymmetric error penalties where False Positives (marking a legitimate email as spam) are 100x more costly than False Negatives.

## Business Context & Loss Matrix
In email security, the business costs of errors are heavily asymmetric:
- **False Positive (Type I Error):** A critical email from a customer, boss, or bank is diverted to the Spam folder. The user misses an important meeting or contract. **Penalty: $100.00**.
- **False Negative (Type II Error):** An annoying unsolicited advertising email lands in the Inbox. The user takes 1 second to delete it. **Penalty: $1.00**.

Because False Positives are 100 times more costly than False Negatives, an off-the-shelf classifier operating at default threshold `tau = 0.50` will fail in production. The threshold must be calibrated on validation data to optimize net business utility.

## Architecture and Requirements

```
Raw Email Stream
  └──> Regex Cleaning & Tokenization (lowercase, strip HTML, punctuation)
        └──> Stopword Filtering & Bigram Extraction
              └──> TF-IDF Vectorization (sublinear TF scaling, min_df=2)
                    └──> Stratified 3-Way Splitting (60% Train / 20% Val / 20% Test)
                          ├──> Model Benchmark: MultinomialNB vs LogisticRegression vs SGDClassifier
                          ├──> Asymmetric Cost Threshold Calibration on Validation Split
                          └──> Gated Single Test Set Sign-Off & Error Audit
```

### 1. Preprocessing & Feature Engineering
- Implement tokenization using `re.findall(r"\b\w+\b", text.lower())`.
- Filter domain-specific stopwords while preserving high-information tokens (`"free"`, `"urgent"`, `"winner"`, `"claim"`, `"invoice"`).
- Extract unigram and bigram token pairs (`ngram_range=(1, 2)`).
- Compute TF-IDF matrices with sublinear term frequency scaling (`sublinear_tf=True`).

### 2. Stratified Model Tournament
Evaluate the following candidate architectures using Stratified 5-Fold Cross-Validation on the training split:
1. **Multinomial Naive Bayes (`alpha=0.1`, `alpha=1.0`)**
2. **Logistic Regression with L2 Regularization (`C=1.0, 10.0`, `class_weight='balanced'`)**
3. **Linear Support Vector Classifier (`LinearSVC(C=1.0)`)**

### 3. Cost-Sensitive Threshold Optimization
On the validation split, sweep decision threshold `tau in [0.01, 0.99]` to find `tau^*` minimizing:

$$\text{Total Cost}(\tau) = 100.0 \times \text{FP}(\tau) + 1.0 \times \text{FN}(\tau)$$

### 4. Gated Final Evaluation
Evaluate the calibrated pipeline on the held-out test split, reporting:
- Precision, Recall, F1 Score, and Matthews Correlation Coefficient (MCC).
- Receiver Operating Characteristic (ROC) and Precision-Recall (PR) curves.
- Detailed confusion matrix breakdown.

---

## Expected output

A successful run of the spam classification pipeline prints the benchmark tournament results, optimal threshold, and final test metrics:

```text
======================================================================
WEEK 23 PROJECT: HIGH-PRECISION SPAM CLASSIFICATION BENCHMARK
======================================================================
Dataset: 5,572 messages (4,825 Ham [86.6%], 747 Spam [13.4%])
Splits: Train=3,343 (60%), Validation=1,114 (20%), Test=1,115 (20%)
Vocabulary: 8,420 unique n-gram features (unigrams + bigrams)

--- 1. Stratified 5-Fold CV Model Tournament ---
• MultinomialNB (alpha=0.1):      Mean CV F1 = 0.9382 | PR AUC = 0.9712
• MultinomialNB (alpha=1.0):      Mean CV F1 = 0.9124 | PR AUC = 0.9605
• LogisticRegression (C=10.0):    Mean CV F1 = 0.9465 | PR AUC = 0.9824  [CHAMPION]
• LinearSVC (C=1.0):              Mean CV F1 = 0.9410 | PR AUC = 0.9780

--- 2. Cost-Sensitive Threshold Calibration on Validation Split ---
Asymmetric Loss Matrix: Cost(FP) = $100.00, Cost(FN) = $1.00
Default Threshold tau = 0.50:  FP=4 ($400), FN=8 ($8)   ==> Total Cost = $408.00
Optimal Threshold tau* = 0.88: FP=0 ($0),   FN=14 ($14) ==> Total Cost = $14.00
Cost Reduction: 96.6% savings achieved through threshold calibration!

--- 3. Final Held-Out Test Set Sign-Off (1,115 messages) ---
Confusion Matrix:
  TN = 965  (Clean Ham)
  FP = 0    (Zero False Alarms: No legitimate email sent to spam!)
  FN = 12   (Spam slipped through)
  TP = 138  (Spam caught)

Test Metrics:
  Accuracy:  0.9892
  Precision: 1.0000 (100.0% Purity)
  Recall:    0.9200
  F1 Score:  0.9583
  MCC:       0.9538
  ROC AUC:   0.9942
  PR AUC:    0.9856
======================================================================
STATUS: CERTIFIED FOR PRODUCTION SERVING
======================================================================
```

---

## Validation

Execute the full project validation pipeline to verify your implementation:

```bash
# 1. Activate your environment
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scikit-learn pytest scipy

# 2. Run the spam classification pipeline
python3 spam_classifier_project.py

# 3. Verify all test assertions
pytest tests/ -v
```

### Self-Check Verification Checklist
1. **Zero Data Leakage:** Ensure `TfidfVectorizer.fit` was called strictly on the training partition (`X_train`), never on the entire corpus.
2. **False Positive Constraint:** Confirm that the calibrated threshold `tau^*` achieves `FP = 0` (or `Precision >= 0.99`) on the test split under the 100:1 cost penalty.
3. **Single Test Touch:** Verify that the test split was evaluated exactly once after all modeling and threshold choices were finalized.
