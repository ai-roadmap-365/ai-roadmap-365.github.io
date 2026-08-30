# Week 31 Project: Custom Image Classifier

## Project overview
In this project, you will build, fine-tune, evaluate, and export a complete, production-grade Custom Image Classifier. You will synthesize all concepts from Week 31: raw image data curation with perceptual hashing (pHash) deduplication, transfer learning from a pretrained convolutional backbone (ResNet-34 / ConvNeXt-Tiny), advanced stochastic data augmentation (`torchvision.transforms.v2` with MixUp / CutMix), Automatic Mixed Precision (AMP) training with `GradScaler`, an automated Error-Case Gallery diagnosing failure modes, and deployment export to ONNX Runtime with dynamic batching.

## Objectives
- Curate and structure a custom multi-class image dataset into stratified train, validation, and test splits with zero duplicate leakage via pHash deduplication.
- Fine-tune a pretrained deep convolutional backbone using a two-stage training regimen: frozen backbone warmup followed by layer-wise differential learning rates.
- Implement stochastic data augmentation including RandomResizedCrop, ColorJitter, RandomHorizontalFlip, and CutMix batch regularization.
- Build an automated Error-Case Gallery script surfacing top high-confidence misclassifications and categorizing errors into label noise, optical occlusion, and taxonomic ambiguity.
- Export the fine-tuned model to ONNX format with dynamic batch axes and verify numerical equivalence (< 1e-5 difference) in ONNX Runtime.

## Architecture
```
[Raw Image Dataset on Disk]
       │
       ▼
[pHash Deduplication & Stratified Split: Train (70%) / Val (15%) / Test (15%)]
       │
       ▼
[torchvision.transforms.v2 Augmentation Pipeline: RandomResizedCrop + ColorJitter + CutMix]
       │
       ▼
[Pretrained ResNet-34 Backbone (Frozen Stem -> Layer-Wise Unfreezing)]
       │
       ▼
[Global Average Pooling + Custom Multi-Class Classifier Head]
       │
       ▼
[Mixed Precision Training (torch.cuda.amp + GradScaler + AdamW + Cosine Warmup)]
       │
       ▼
[Multi-Metric Evaluation: Top-1/Top-5 Accuracy + Macro F1 + Confusion Matrix]
       │
       ▼
[Error-Case Gallery Diagnostics + ONNX Runtime Export Deployment]
```

## Implementation guidelines
1. **Data Curation & Deduplication:** Run perceptual hashing (pHash) across all candidate images. Eliminate near-duplicate image pairs with Hamming distance <= 3 to prevent train/val leakage.
2. **Transfer Learning Setup:** Instantiate a pretrained ResNet-34 model (`weights="DEFAULT"`). Replace the final classification head with a custom linear projection matching your dataset class count.
3. **Two-Stage Fine-Tuning:**
   - *Phase 1 (Warmup):* Freeze all backbone weights (`requires_grad = False`). Train only the custom head for 3 epochs with $LR = 10^{-3}$.
   - *Phase 2 (Differential Tuning):* Unfreeze deeper residual stages. Train with differential learning rates (Backbone $LR = 10^{-5}$, Head $LR = 10^{-4}$) with Cosine Annealing decay over 15 epochs.
4. **Data Augmentation:** Apply stochastic `v2.Compose` transforms during training and deterministic CenterCrop during validation.
5. **Error-Case Gallery:** Implement an automated inspection function that ranks validation misclassifications by prediction confidence, displaying true label, predicted label, and confidence score.
6. **ONNX Export & Verification:** Export model to `custom_image_classifier.onnx` with dynamic batch axis and verify numerical alignment in `onnxruntime`.

## Expected output
```
[Custom Image Classifier Pipeline Verification]
1. Data Curation & Deduplication:
   - Scanned 2,400 raw images across 6 classes.
   - Identified and removed 48 near-duplicate images (pHash Hamming distance <= 3).
   - Partitioned into 1,648 train, 352 val, and 352 test samples.
2. Two-Stage Fine-Tuning Execution:
   - Phase 1 (Head Warmup - 3 epochs): Val Top-1 Accuracy = 86.4%
   - Phase 2 (Differential Fine-Tuning - 15 epochs): Val Top-1 Accuracy = 94.8%, Top-5 Accuracy = 99.4%
3. Error-Case Gallery Diagnostic Report:
   - Surfaced top 5 confident misclassifications.
   - Identified 2 ground-truth human annotation errors in validation set.
4. Production Export:
   - Exported to custom_image_classifier.onnx (84.2 MB).
   - Verified ONNX Runtime numerical max logit error: 1.192e-07.
```

## Validation
To validate your implementation:
1. Verify that pHash deduplication removes all exact and near-duplicate images.
2. Confirm that Phase 1 keeps backbone weights strictly frozen (`grad is None`).
3. Ensure final validation Top-1 accuracy achieves >= 92.0% on your dataset.
4. Verify that ONNX export passes numerical parity validation in ONNX Runtime.

## Deliverables
- Complete Python training pipeline `custom_image_classifier.py`.
- Automated Error-Case Gallery script `generate_error_gallery.py`.
- Serialized ONNX production artifact `custom_image_classifier.onnx`.
- Diagnostic report detailing dataset statistics, confusion matrix, and error analysis.
