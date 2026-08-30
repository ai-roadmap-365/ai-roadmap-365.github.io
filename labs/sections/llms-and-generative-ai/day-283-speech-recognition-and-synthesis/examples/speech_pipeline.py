# Speech AI: Mel Spectrogram Extractor, CTC Decoder, and WER Evaluator
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

class SpeechPipeline:
    """Audio feature extraction, CTC decoding, and Word Error Rate evaluation."""

    @staticmethod
    def extract_mel_spectrogram(waveform: np.ndarray, num_mel_bins: int = 80, hop_length: int = 160) -> np.ndarray:
        """
        Simulates 80-channel Log-Mel Spectrogram extraction from 1D waveform (16kHz).
        waveform: 1D array of floats
        Returns: (num_mel_bins, num_frames)
        """
        if waveform.ndim != 1:
            waveform = waveform.flatten()

        num_samples = len(waveform)
        num_frames = max(1, num_samples // hop_length)

        # Generate synthetic log-mel energy distribution
        mel_spec = np.zeros((num_mel_bins, num_frames), dtype=np.float32)
        for i in range(num_frames):
            frame = waveform[i * hop_length : min((i + 1) * hop_length, num_samples)]
            energy = np.sum(frame ** 2) if len(frame) > 0 else 0.0
            # Populate filterbanks with decaying frequency response
            for m in range(num_mel_bins):
                mel_spec[m, i] = np.log(1.0 + energy * np.exp(-m / 20.0) + 1e-6)

        return mel_spec

    @staticmethod
    def ctc_greedy_decode(logits: np.ndarray, vocab: List[str], blank_index: int = 0) -> str:
        """
        Performs CTC greedy collapse: argmax -> collapse consecutive duplicates -> strip blanks.
        logits: (Time_Frames, Vocab_Size)
        """
        best_tokens = np.argmax(logits, axis=-1)
        
        collapsed = []
        prev = None
        for token in best_tokens:
            if token != prev:
                if token != blank_index and token < len(vocab):
                    collapsed.append(vocab[token])
                prev = token

        return "".join(collapsed)

    @staticmethod
    def compute_wer(reference: str, hypothesis: str) -> float:
        """Computes exact Levenshtein Word Error Rate (WER)."""
        ref_words = reference.strip().split()
        hyp_words = hypothesis.strip().split()

        if not ref_words:
            return 0.0 if not hyp_words else 1.0

        d = np.zeros((len(ref_words) + 1, len(hyp_words) + 1), dtype=np.int32)
        for i in range(len(ref_words) + 1):
            d[i, 0] = i
        for j in range(len(hyp_words) + 1):
            d[0, j] = j

        for i in range(1, len(ref_words) + 1):
            for j in range(1, len(hyp_words) + 1):
                if ref_words[i - 1] == hyp_words[j - 1]:
                    d[i, j] = d[i - 1, j - 1]
                else:
                    d[i, j] = min(
                        d[i - 1, j] + 1,      # Deletion
                        d[i, j - 1] + 1,      # Insertion
                        d[i - 1, j - 1] + 1   # Substitution
                    )

        return float(d[len(ref_words), len(hyp_words)]) / float(len(ref_words))
