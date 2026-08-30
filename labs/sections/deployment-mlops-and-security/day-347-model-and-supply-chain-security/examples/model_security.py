import os
import json
import hashlib
from typing import Dict, Any, List, Tuple

class ModelSupplyChainScanner:
    def __init__(self, allowed_extensions: Tuple[str, ...] = (".safetensors", ".json", ".txt")):
        self.allowed_extensions = allowed_extensions

    def calculate_sha256(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    def scan_model_directory(self, dir_path: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        findings: List[str] = []
        is_compliant = True
        artifacts: List[Dict[str, Any]] = []

        if not os.path.exists(dir_path):
            return False, [f"Directory not found: {dir_path}"], {}

        for root, _, files in os.walk(dir_path):
            for file in sorted(files):
                full_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()

                if ext in [".pt", ".bin", ".pkl", ".joblib", ".pickle"]:
                    is_compliant = False
                    findings.append(f"CRITICAL: Insecure serialized format detected: {file} ({ext}). Must convert to .safetensors.")

                if ext not in self.allowed_extensions:
                    findings.append(f"WARNING: Unrecognized file extension in model bundle: {file}")

                file_hash = self.calculate_sha256(full_path)
                file_size = os.path.getsize(full_path)
                artifacts.append({
                    "filename": file,
                    "relative_path": os.path.relpath(full_path, dir_path),
                    "size_bytes": file_size,
                    "sha256": file_hash,
                    "format": "safetensors" if ext == ".safetensors" else "metadata"
                })

        aibom = {
            "bom_format": "CycloneDX-AI",
            "spec_version": "1.5",
            "model_name": os.path.basename(dir_path.rstrip("/\\")),
            "compliant": is_compliant,
            "total_artifacts": len(artifacts),
            "artifacts": artifacts
        }

        return is_compliant, findings, aibom

if __name__ == "__main__":
    s = ModelSupplyChainScanner()
    print("Scanner ready.")
