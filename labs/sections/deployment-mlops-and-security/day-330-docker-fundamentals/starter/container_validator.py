import os
import json
from typing import Dict, Any, List, Optional

class ContainerEnvironmentValidator:
    def __init__(self, target_image_type: str = "production_runtime"):
        self.image_type = target_image_type
        self.installed_packages: Dict[str, str] = {}
        self.gpu_devices: List[str] = []
        self.vram_gb: int = 0
        self.is_running_as_non_root: bool = False
        
    def simulate_build_stage(self, stage: str, wheels_built: List[str]):
        if stage == "builder":
            self.installed_packages["build_tools"] = "DISCARDED"
            for w in wheels_built:
                self.installed_packages[w] = "COMPILED_WHEEL"
        elif stage == "runner":
            self.installed_packages = {k: v for k, v in self.installed_packages.items() if v == "COMPILED_WHEEL"}
            self.is_running_as_non_root = True

    def configure_gpu_devices(self, devices: List[str], vram_per_device_gb: int = 24):
        self.gpu_devices = devices
        self.vram_gb = vram_per_device_gb

    def verify_readiness_probe(self) -> Dict[str, Any]:
        if not self.gpu_devices:
            return {"status": "NOT_READY", "reason": "NO_GPU_DEVICES_DETECTED", "http_code": 503}
            
        if not self.is_running_as_non_root:
            return {"status": "SECURITY_WARNING", "reason": "RUNNING_AS_ROOT", "http_code": 500}
            
        return {
            "status": "READY",
            "http_code": 200,
            "gpu_count": len(self.gpu_devices),
            "vram_allocated_gb": len(self.gpu_devices) * self.vram_gb,
            "security_context": "NON_ROOT_USER"
        }

if __name__ == "__main__":
    v = ContainerEnvironmentValidator()
    v.simulate_build_stage("builder", ["torch", "vllm"])
    v.simulate_build_stage("runner", [])
    v.configure_gpu_devices(["/dev/nvidia0"], 24)
    print(v.verify_readiness_probe())
