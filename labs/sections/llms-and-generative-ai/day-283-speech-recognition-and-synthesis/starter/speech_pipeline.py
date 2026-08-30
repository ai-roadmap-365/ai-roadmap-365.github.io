# Starter: Speech Pipeline
import numpy as np
from typing import List

class SpeechPipeline:
    @staticmethod
    def extract_mel_spectrogram(waveform: np.ndarray, num_mel_bins: int = 80, hop_length: int = 160) -> np.ndarray:
        return np.zeros((num_mel_bins, 10), dtype=np.float32)

    @staticmethod
    def ctc_greedy_decode(logits: np.ndarray, vocab: List[str], blank_index: int = 0) -> str:
        return ""

    @staticmethod
    def compute_wer(reference: str, hypothesis: str) -> float:
        return 0.0
