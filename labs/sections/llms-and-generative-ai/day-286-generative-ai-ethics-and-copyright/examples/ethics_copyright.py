# Generative AI Ethics & Copyright: pHash Engine and C2PA Manifest Verifier
import hashlib
import json
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

class EthicsComplianceEngine:
    """Perceptual hashing, Hamming distance, and C2PA manifest verification."""

    @staticmethod
    def compute_phash(image_gray: np.ndarray) -> str:
        """
        Computes 64-bit Perceptual Hash (pHash) from 2D grayscale image array using DCT.
        image_gray: (H, W) array of floats
        """
        if image_gray.ndim != 2:
            raise ValueError(f"Expected 2D grayscale array, got shape {image_gray.shape}")

        h, w = image_gray.shape
        # Bilinear resize to 32x32
        y_idx = np.linspace(0, h - 1, 32).astype(np.int32)
        x_idx = np.linspace(0, w - 1, 32).astype(np.int32)
        resized = image_gray[np.ix_(y_idx, x_idx)].astype(np.float32)

        # 2D DCT
        n = 32
        i = np.arange(n).reshape(-1, 1)
        j = np.arange(n).reshape(1, -1)
        dct_matrix = np.cos((2.0 * i + 1.0) * j * np.pi / (2.0 * n))
        dct = dct_matrix.T @ resized @ dct_matrix

        # Top-left 8x8 low frequencies
        low_freq = dct[:8, :8]
        median_val = np.median(low_freq)

        bits = (low_freq > median_val).astype(np.int32).flatten()
        # Convert 64 bits to 16-char hex string
        bit_str = "".join(map(str, bits))
        val = int(bit_str, 2)
        return f"{val:016x}"

    @staticmethod
    def compute_hamming_distance(hash1_hex: str, hash2_hex: str) -> int:
        """Computes number of differing bits between two 64-bit hex hashes."""
        val1 = int(hash1_hex, 16)
        val2 = int(hash2_hex, 16)
        return bin(val1 ^ val2).count('1')

    @staticmethod
    def create_c2pa_manifest(media_bytes: bytes, author: str, generator_tool: str) -> Dict[str, Any]:
        """Constructs a signed C2PA provenance manifest."""
        payload_hash = hashlib.sha256(media_bytes).hexdigest()
        claim = {
            "title": "C2PA Provenance Manifest",
            "format": "application/c2pa",
            "claim_generator": generator_tool,
            "author": author,
            "assertions": [
                {"label": "c2pa.actions", "action": "c2pa.created"},
                {"label": "c2pa.ai_generative", "software": generator_tool}
            ],
            "target_hash_sha256": payload_hash
        }
        # Simulated digital signature
        claim_json = json.dumps(claim, sort_keys=True)
        signature = hashlib.sha256((claim_json + "_CERTIFICATE_SECRET").encode('utf-8')).hexdigest()
        
        return {
            "claim": claim,
            "signature": signature
        }

    @staticmethod
    def verify_c2pa_manifest(manifest: Dict[str, Any], media_bytes: bytes) -> bool:
        """Verifies cryptographic binding between manifest and media payload."""
        claim = manifest.get("claim", {})
        expected_hash = claim.get("target_hash_sha256")
        actual_hash = hashlib.sha256(media_bytes).hexdigest()

        if expected_hash != actual_hash:
            return False

        # Verify signature integrity
        claim_json = json.dumps(claim, sort_keys=True)
        expected_sig = hashlib.sha256((claim_json + "_CERTIFICATE_SECRET").encode('utf-8')).hexdigest()
        return manifest.get("signature") == expected_sig

    @staticmethod
    def audit_memorization_risk(candidate_hash: str, reference_database: List[Dict[str, str]], threshold_distance: int = 5) -> List[Dict[str, Any]]:
        """Scans candidate hash against database of protected copyright works."""
        violations = []
        for entry in reference_database:
            dist = EthicsComplianceEngine.compute_hamming_distance(candidate_hash, entry["phash"])
            if dist <= threshold_distance:
                violations.append({
                    "matched_id": entry["id"],
                    "title": entry["title"],
                    "hamming_distance": dist,
                    "risk_severity": "CRITICAL" if dist <= 2 else "HIGH"
                })
        return violations
