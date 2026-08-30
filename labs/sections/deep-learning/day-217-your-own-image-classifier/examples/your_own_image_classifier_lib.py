import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, Dict, Any, List

def calculate_simple_phash(img_gray: np.ndarray) -> str:
    # img_gray: 2D numpy array
    # Resize to 8x8 average
    h, w = img_gray.shape
    h_step, w_step = h // 8, w // 8
    small = np.zeros((8, 8), dtype=np.float32)
    for i in range(8):
        for j in range(8):
            small[i, j] = np.mean(img_gray[i*h_step:(i+1)*h_step, j*w_step:(j+1)*w_step])

    avg = np.mean(small)
    bits = (small > avg).flatten()
    return "".join(["1" if b else "0" for b in bits])

def hamming_distance(hash1: str, hash2: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

def generate_error_gallery(logits: torch.Tensor, targets: torch.Tensor,
                           class_names: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
    with torch.no_grad():
        probs = torch.softmax(logits, dim=1)
        confidences, preds = torch.max(probs, dim=1)
        incorrect = preds != targets

        failures = []
        for i in range(targets.size(0)):
            if incorrect[i]:
                true_idx = targets[i].item()
                pred_idx = preds[i].item()
                conf = confidences[i].item()
                failures.append({
                    "sample_idx": i,
                    "true_class": class_names[true_idx],
                    "pred_class": class_names[pred_idx],
                    "confidence": conf,
                    "true_prob": probs[i, true_idx].item()
                })

        failures.sort(key=lambda x: x["confidence"], reverse=True)
        return failures[:top_n]

def run_classifier_audit_demo():
    torch.manual_seed(42)
    np.random.seed(42)

    img1 = np.random.rand(32, 32).astype(np.float32)
    img2 = img1.copy()
    img2[0, 0] = 0.0 # Minor edit

    h1 = calculate_simple_phash(img1)
    h2 = calculate_simple_phash(img2)
    dist = hamming_distance(h1, h2)

    logits = torch.tensor([
        [5.0, 0.1, 0.2],
        [0.1, 4.0, 0.5],
        [0.2, 3.5, 0.1] # Sample 2: pred=1, true=0 (conf=96.7% error!)
    ])
    targets = torch.tensor([0, 1, 0])
    class_names = ["Chamomile", "Peppermint", "Hibiscus"]

    gallery = generate_error_gallery(logits, targets, class_names, top_n=2)
    print(f"Classifier Audit Demo: pHash Dist = {dist}, Top Error = {gallery[0]['pred_class']} (Conf: {gallery[0]['confidence']:.2f})")
    return dist, gallery

if __name__ == "__main__":
    run_classifier_audit_demo()
