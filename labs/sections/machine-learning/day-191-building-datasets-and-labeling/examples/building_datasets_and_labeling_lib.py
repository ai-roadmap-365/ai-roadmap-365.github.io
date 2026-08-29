import numpy as np

def compute_shannon_entropy(probs: np.ndarray) -> np.ndarray:
    clipped = np.clip(probs, 1e-12, 1.0)
    return -np.sum(clipped * np.log2(clipped), axis=1)

def compute_cohen_kappa(y1: np.ndarray, y2: np.ndarray) -> float:
    assert len(y1) == len(y2)
    classes = np.unique(np.concatenate([y1, y2]))
    p_o = float(np.mean(y1 == y2))

    p_e = 0.0
    for c in classes:
        p1 = float(np.mean(y1 == c))
        p2 = float(np.mean(y2 == c))
        p_e += p1 * p2

    if np.isclose(p_e, 1.0):
        return 1.0
    return float((p_o - p_e) / (1.0 - p_e))

class MajorityVoteLabelModel:
    def __init__(self, abstain_val: int = 0):
        self.abstain_val = abstain_val

    def fit_predict(self, L: np.ndarray) -> np.ndarray:
        n_samples = L.shape[0]
        y_pred = np.zeros(n_samples, dtype=int)
        for i in range(n_samples):
            row_votes = L[i, L[i] != self.abstain_val]
            if len(row_votes) == 0:
                y_pred[i] = 0
            else:
                vote_sum = np.sum(row_votes)
                y_pred[i] = 1 if vote_sum > 0 else (-1 if vote_sum < 0 else 0)
        return y_pred

def run_labeling_demo():
    np.random.seed(42)
    probs = np.array([
        [0.51, 0.49], # High entropy
        [0.95, 0.05], # Low entropy
        [0.48, 0.52], # High entropy
        [0.88, 0.12]  # Low entropy
    ])
    entropy = compute_shannon_entropy(probs)
    print(f"Data Engine Demo: Max Entropy = {np.max(entropy):.4f}")
    return entropy

if __name__ == "__main__":
    run_labeling_demo()
