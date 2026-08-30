import os
import tempfile
import pytest
from examples.model_security import ModelSupplyChainScanner

def test_insecure_pickle_format_detected():
    scanner = ModelSupplyChainScanner()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create insecure .pt file
        with open(os.path.join(tmpdir, "weights.pt"), "wb") as f:
            f.write(b"fake pickle payload")
            
        compliant, findings, aibom = scanner.scan_model_directory(tmpdir)
        assert compliant is False
        assert any("CRITICAL: Insecure serialized format detected" in f for f in findings)
        assert aibom["compliant"] is False

def test_safetensors_compliance():
    scanner = ModelSupplyChainScanner()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create safe safetensors file
        with open(os.path.join(tmpdir, "model.safetensors"), "wb") as f:
            f.write(b"safetensors data buffer")
        with open(os.path.join(tmpdir, "config.json"), "w") as f:
            f.write('{"vocab_size": 32000}')
            
        compliant, findings, aibom = scanner.scan_model_directory(tmpdir)
        assert compliant is True
        assert len(findings) == 0
        assert aibom["compliant"] is True
        assert aibom["total_artifacts"] == 2

def test_sha256_hash_calculation():
    scanner = ModelSupplyChainScanner()
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "wb") as f:
            f.write(b"hello world")
            
        # SHA256 for 'hello world' is b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
        h = scanner.calculate_sha256(test_file)
        assert h == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

def test_aibom_manifest_structure():
    scanner = ModelSupplyChainScanner()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "weights.safetensors"), "wb") as f:
            f.write(b"bytes")
            
        _, _, aibom = scanner.scan_model_directory(tmpdir)
        assert aibom["bom_format"] == "CycloneDX-AI"
        assert "artifacts" in aibom
        assert aibom["artifacts"][0]["filename"] == "weights.safetensors"
        assert aibom["artifacts"][0]["format"] == "safetensors"

def test_nonexistent_directory():
    scanner = ModelSupplyChainScanner()
    compliant, findings, aibom = scanner.scan_model_directory("/path/to/nonexistent/dir/12345")
    assert compliant is False
    assert "Directory not found" in findings[0]
