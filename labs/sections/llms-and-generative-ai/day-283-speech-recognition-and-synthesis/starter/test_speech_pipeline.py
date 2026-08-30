import pytest
import numpy as np
from speech_pipeline import SpeechPipeline

def test_mel_spectrogram_dimensions():
    # 1.0 second of audio at 16,000 Hz = 16,000 samples
    waveform = np.sin(np.linspace(0, 100, 16000)).astype(np.float32)
    mel_spec = SpeechPipeline.extract_mel_spectrogram(waveform, num_mel_bins=80, hop_length=160)
    
    assert mel_spec.shape == (80, 100) # 80 mel channels, 100 time frames
    assert not np.isnan(mel_spec).any()
    assert np.all(mel_spec >= 0.0)

def test_ctc_greedy_decode_collapse():
    vocab = ["<blank>", "h", "e", "l", "o", " ", "w", "r", "d"]
    # Simulate frame predictions for "h-h-e-l-l-l-o" -> "hello"
    # Token indices: h=1, e=2, l=3, o=4, blank=0
    indices = [1, 1, 0, 2, 2, 3, 3, 3, 0, 4, 4]
    
    logits = np.zeros((len(indices), len(vocab)), dtype=np.float32)
    for t, idx in enumerate(indices):
        logits[t, idx] = 10.0 # High confidence logit
        
    transcript = SpeechPipeline.ctc_greedy_decode(logits, vocab, blank_index=0)
    assert transcript == "helo"

def test_ctc_all_blanks():
    vocab = ["<blank>", "a", "b"]
    logits = np.zeros((5, 3), dtype=np.float32)
    logits[:, 0] = 10.0 # All blank
    
    transcript = SpeechPipeline.ctc_greedy_decode(logits, vocab, blank_index=0)
    assert transcript == ""

def test_wer_exact_match():
    ref = "the quick brown fox"
    hyp = "the quick brown fox"
    wer = SpeechPipeline.compute_wer(ref, hyp)
    assert wer == 0.0

def test_wer_substitutions_and_deletions():
    ref = "the quick brown fox jumps"
    # "the quik fox" -> 1 substitution ('quick'->'quik'), 1 deletion ('brown'), 1 deletion ('jumps')
    # Total errors = 3 / 5 words = 0.60
    hyp = "the quik fox"
    wer = SpeechPipeline.compute_wer(ref, hyp)
    assert wer == pytest.approx(0.60, 0.01)

def test_wer_empty_strings():
    assert SpeechPipeline.compute_wer("", "") == 0.0
    assert SpeechPipeline.compute_wer("hello world", "") == 1.0
