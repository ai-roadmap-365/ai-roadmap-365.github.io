# Week 32 Project: Sentiment Analyzer

## Project overview
In this project, you will design, implement, rigorously benchmark, explain, and deploy a production-grade Sentiment Analysis system. You will synthesize the entire curriculum of Week 32: text normalization and subword tokenization, pretrained word embeddings (GloVe/FastText), building and comparing three distinct model families (TF-IDF Baseline, fastText `EmbeddingBag`, and Bidirectional LSTM with learned Attention Pooling), evaluating performance with Macro F1, ROC-AUC, and Expected Calibration Error (ECE), extracting token-level Integrated Gradients explainability attributions, and serving real-time predictions via an ONNX Runtime microservice.

## Objectives
- Implement a robust text data preprocessing pipeline with regex normalization, contraction expansion, vocabulary collation, and dynamic batch padding.
- Build, train, and evaluate three candidate model architectures under identical data splits:
  1. *Baseline:* TF-IDF n-gram vectorizer with Logistic Regression.
  2. *Neural BoW:* FastText-style `nn.EmbeddingBag` with mean pooling.
  3. *Sequential:* Bidirectional LSTM with Multi-Head Attention Pooling.
- Evaluate models using comprehensive metrics: Accuracy, Precision, Recall, Macro F1-Score, ROC-AUC curves, confusion matrices, and Expected Calibration Error (ECE).
- Implement an automated model explainability module using Integrated Gradients to produce token-level attribution heatmaps for positive and negative review predictions.
- Export the top-performing model to ONNX format with dynamic batch axes and benchmark CPU latency against throughput requirements.

## Architecture
```
[Raw Customer Reviews / Tweets Dataset]
                  │
                  ▼
[Text Preprocessing: Regex Cleaning + Contraction Expansion + Tokenization]
                  │
                  ▼
[Vocabulary Construction (Min Freq = 3, Vocab Size = 25,000, Special Tokens)]
                  │
                  ▼
[Dynamic Collate Pipeline: Stratified Split (Train 70% / Val 15% / Test 15%)]
                  │
                  ├───► [Model 1: TF-IDF + Logistic Regression Baseline]
                  ├───► [Model 2: PyTorch nn.EmbeddingBag Mean Pooling]
                  └───► [Model 3: PyTorch BiLSTM + Learned Attention Pooling]
                                      │
                                      ▼
                      [Multi-Metric Comparative Evaluation]
                      - Macro F1-Score & ROC-AUC Curves
                      - Expected Calibration Error (ECE)
                      - Inference Latency vs Parameter Count
                                      │
                                      ▼
                      [Model Explainability & Serving]
                      - Integrated Gradients Token Saliency
                      - ONNX Runtime Export (< 1.5 ms Latency)
```

## Implementation guidelines
1. **Data Ingestion & Preprocessing:**
   - Ingest raw text reviews. Apply regex cleaning to remove HTML tags, URLs, and noisy control characters.
   - Standardize contractions (`"don't"` -> `"do not"`).
   - Build a vocabulary dictionary mapping unique words to indices, reserving IDs for `<pad>`, `<unk>`, `<bos>`, and `<eos>`.
2. **DataLoader & Dynamic Collate:**
   - Implement a custom `collate_fn` in PyTorch that dynamically pads each batch only to the length of the longest sentence in that specific batch.
3. **Model Implementation:**
   - Build `EmbeddingBagClassifier`: uses `nn.EmbeddingBag(mode="mean")` with a linear classification head and Dropout ($p=0.5$).
   - Build `BiLSTMAttentionSentiment`: incorporates a 2-layer Bidirectional LSTM, computes learned dynamic attention alignment scores over all hidden states, and pools features into a dense classification head.
4. **Training & Optimization:**
   - Train both neural models using AdamW optimizer ($\eta = 10^{-3}$, weight decay $= 10^{-4}$), CrossEntropyLoss with label smoothing ($\epsilon = 0.05$), and Cosine Annealing learning rate schedule.
5. **Model Evaluation & Diagnostics:**
   - Calculate Precision, Recall, and Macro F1-score across validation and test sets.
   - Compute Expected Calibration Error (ECE) across 10 confidence bins.
   - Profile average forward-pass latency per sample on CPU over 1,000 iterations.
6. **Token Attribution Explainability:**
   - Implement Integrated Gradients or input-embedding gradient saliency to extract word-level importance scores.
   - Output visual attribution maps highlighting positive sentiment drivers in green and negative drivers in red.
7. **ONNX Export:**
   - Export the best neural model to `sentiment_analyzer.onnx` with dynamic batch and sequence axes. Verify numerical equivalence in `onnxruntime`.

## Expected output
```
[Sentiment Analyzer System Benchmark Report]
1. Dataset & Preprocessing:
   - Total Reviews Ingested: 25,000 (12,500 Positive, 12,500 Negative)
   - Vocabulary Size: 24,812 tokens (pruned min_freq >= 3)
   - Splits: 17,500 Train | 3,750 Validation | 3,750 Test
2. Multi-Model Benchmark Comparison:
   +--------------------+----------+----------+---------+---------+------------+
   | Model Architecture | Accuracy | Macro F1 | ROC-AUC | ECE (%) | Latency/Ex |
   +--------------------+----------+----------+---------+---------+------------+
   | TF-IDF + LogReg    | 88.4%    | 0.883    | 0.942   | 4.8%    | 0.08 ms    |
   | nn.EmbeddingBag    | 89.6%    | 0.895    | 0.954   | 3.9%    | 0.15 ms    |
   | BiLSTM + Attention | 93.8%    | 0.937    | 0.981   | 2.1%    | 1.42 ms    |
   +--------------------+----------+----------+---------+---------+------------+
3. Explainability Diagnostics (Integrated Gradients):
   - Sample: "The battery life is fantastic and screen is gorgeous, but setup was confusing."
   - Positive Drivers: "fantastic" (+0.84), "gorgeous" (+0.72)
   - Negative Drivers: "confusing" (-0.61)
   - Overall Prediction: 89.2% Positive (Verified Attention Focus on Contrastive Clause)
4. Production Export:
   - Exported to sentiment_analyzer.onnx (6.4 MB).
   - ONNX Runtime verification max absolute difference: 2.384e-07 [PASSED].
```

## Validation
To validate your implementation:
1. Verify that dynamic batch collation executes without padding leakage.
2. Confirm that `BiLSTMAttentionSentiment` achieves Macro F1 >= 0.90 on the test split.
3. Ensure token attribution scores sum to the prediction delta within 5% tolerance (Completeness check).
4. Verify that the exported ONNX model loads cleanly and matches PyTorch outputs in ONNX Runtime.

## Deliverables
- Complete training pipeline `sentiment_analyzer.py`.
- Explainability attribution module `explainability.py`.
- Serialized model artifact `sentiment_analyzer.onnx`.
- Benchmark evaluation report and calibration diagnostic plots.
