import pytest
import numpy as np
from ethics_copyright import EthicsComplianceEngine

def test_phash_deterministic():
    img = np.zeros((64, 64), dtype=np.float32)
    img[20:40, 20:40] = 1.0 # White square in center
    
    hash1 = EthicsComplianceEngine.compute_phash(img)
    hash2 = EthicsComplianceEngine.compute_phash(img)
    
    assert len(hash1) == 16
    assert hash1 == hash2

def test_phash_near_duplicate_tolerance():
    img1 = np.zeros((64, 64), dtype=np.float32)
    img1[20:40, 20:40] = 1.0
    
    # img2 is slightly noisy version of img1
    np.random.seed(42)
    img2 = img1 + np.random.randn(64, 64).astype(np.float32) * 0.05
    
    hash1 = EthicsComplianceEngine.compute_phash(img1)
    hash2 = EthicsComplianceEngine.compute_phash(img2)
    
    dist = EthicsComplianceEngine.compute_hamming_distance(hash1, hash2)
    assert dist <= 5 # Low hamming distance confirms near-duplicate

def test_c2pa_manifest_roundtrip():
    payload = b"FAKE_SYNTHETIC_IMAGE_BYTES_RGBA"
    manifest = EthicsComplianceEngine.create_c2pa_manifest(payload, author="Alice", generator_tool="Diffusion-v1")
    
    assert EthicsComplianceEngine.verify_c2pa_manifest(manifest, payload) is True

def test_c2pa_tamper_detection():
    payload = b"ORIGINAL_IMAGE_BYTES"
    manifest = EthicsComplianceEngine.create_c2pa_manifest(payload, author="Alice", generator_tool="Diffusion-v1")
    
    tampered_payload = b"TAMPERED_IMAGE_BYTES"
    assert EthicsComplianceEngine.verify_c2pa_manifest(manifest, tampered_payload) is False

def test_memorization_risk_audit():
    ref_db = [
        {"id": "WORK_001", "title": "Famous Cartoon Character", "phash": "ffff0000ffff0000"},
        {"id": "WORK_002", "title": "Corporate Logo", "phash": "0000ffff0000ffff"}
    ]
    
    # Candidate identical to WORK_001 with 1 bit flip
    candidate = "ffff0000ffff0001"
    violations = EthicsComplianceEngine.audit_memorization_risk(candidate, ref_db, threshold_distance=5)
    
    assert len(violations) == 1
    assert violations[0]["matched_id"] == "WORK_001"
    assert violations[0]["hamming_distance"] == 1
    assert violations[0]["risk_severity"] == "CRITICAL"
