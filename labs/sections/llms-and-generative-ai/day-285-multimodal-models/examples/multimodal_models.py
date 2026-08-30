# Multimodal Models: CLIP InfoNCE Loss, MLP Projector, and Zero-Shot Classifier
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

class MultimodalPipeline:
    """CLIP InfoNCE loss, MLP Multimodal Projector, and Zero-Shot Classification."""

    @staticmethod
    def compute_clip_infonce_loss(image_embeddings: np.ndarray, text_embeddings: np.ndarray, temperature: float = 0.07) -> Tuple[float, np.ndarray]:
        """
        Computes symmetric InfoNCE loss for a batch of N image-text pairs.
        """
        if image_embeddings.shape != text_embeddings.shape:
            raise ValueError(f"Shape mismatch: {image_embeddings.shape} vs {text_embeddings.shape}")

        n = len(image_embeddings)
        if n == 0:
            return 0.0, np.zeros((0, 0), dtype=np.float32)

        # 1. L2 Normalize
        img_norm = image_embeddings / (np.linalg.norm(image_embeddings, axis=-1, keepdims=True) + 1e-12)
        txt_norm = text_embeddings / (np.linalg.norm(text_embeddings, axis=-1, keepdims=True) + 1e-12)

        # 2. Similarity Matrix scaled by temperature
        logits = (img_norm @ txt_norm.T) / float(temperature)
        targets = np.arange(n)

        # 3. Symmetric Cross Entropy
        def cross_entropy(l):
            exp_l = np.exp(l - np.max(l, axis=-1, keepdims=True))
            probs = exp_l / np.sum(exp_l, axis=-1, keepdims=True)
            return -np.mean(np.log(probs[np.arange(n), targets] + 1e-12))

        loss_i2t = cross_entropy(logits)
        loss_t2i = cross_entropy(logits.T)
        total_loss = float(0.5 * (loss_i2t + loss_t2i))

        return total_loss, logits.astype(np.float32)

    @staticmethod
    def zero_shot_classify(image_embedding: np.ndarray, class_text_embeddings: np.ndarray, class_labels: List[str]) -> Dict[str, Any]:
        """
        Classifies single image embedding against candidate class text embeddings using cosine similarity.
        """
        img_norm = image_embedding / (np.linalg.norm(image_embedding) + 1e-12)
        txt_norm = class_text_embeddings / (np.linalg.norm(class_text_embeddings, axis=-1, keepdims=True) + 1e-12)

        similarities = (img_norm @ txt_norm.T).flatten()
        # Softmax probabilities
        exp_s = np.exp(similarities - np.max(similarities))
        probs = exp_s / np.sum(exp_s)

        best_idx = int(np.argmax(probs))
        return {
            "predicted_label": class_labels[best_idx],
            "confidence": float(probs[best_idx]),
            "probabilities": {class_labels[i]: float(probs[i]) for i in range(len(class_labels))}
        }

    @staticmethod
    def project_visual_tokens(visual_tokens: np.ndarray, w1: np.ndarray, b1: np.ndarray, w2: np.ndarray, b2: np.ndarray) -> np.ndarray:
        """
        2-Layer MLP Projector with GELU activation: (B, N_patches, Vision_Dim) -> (B, N_patches, LLM_Dim)
        """
        # Layer 1
        h1 = visual_tokens @ w1 + b1
        # Approximate GELU
        h1_gelu = 0.5 * h1 * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (h1 + 0.044715 * (h1 ** 3))))
        # Layer 2
        h2 = h1_gelu @ w2 + b2
        return h2.astype(np.float32)

    @staticmethod
    def calculate_visual_token_count(image_size: int, patch_size: int = 14) -> int:
        """Calculates number of visual tokens for a square image."""
        grid_dim = image_size // patch_size
        return grid_dim * grid_dim
