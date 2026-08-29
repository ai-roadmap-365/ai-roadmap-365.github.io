import numpy as np

def compute_shannon_entropy(probs: np.ndarray) -> np.ndarray:
    # TODO: Calculate Shannon entropy H(p) = -sum(p * log2(p)) per sample
    pass

def compute_cohen_kappa(y1: np.ndarray, y2: np.ndarray) -> float:
    # TODO: Calculate Cohen's Kappa inter-annotator agreement
    pass

class MajorityVoteLabelModel:
    def __init__(self, abstain_val: int = 0):
        self.abstain_val = abstain_val

    def fit_predict(self, L: np.ndarray) -> np.ndarray:
        # TODO: Aggregate LF matrix L into consensus labels
        pass
