import pytest
from examples.container_validator import ContainerEnvironmentValidator

def test_multi_stage_purges_build_tools():
    v = ContainerEnvironmentValidator()
    v.simulate_build_stage("builder", ["torch-2.4.0", "vllm-0.6.0"])
    assert "build_tools" in v.installed_packages
    
    v.simulate_build_stage("runner", [])
    assert "build_tools" not in v.installed_packages
    assert "torch-2.4.0" in v.installed_packages
    assert v.is_running_as_non_root is True

def test_readiness_probe_success():
    v = ContainerEnvironmentValidator()
    v.simulate_build_stage("builder", ["torch"])
    v.simulate_build_stage("runner", [])
    v.configure_gpu_devices(["/dev/nvidia0", "/dev/nvidia1"], vram_per_device_gb=80)
    
    res = v.verify_readiness_probe()
    assert res["status"] == "READY"
    assert res["http_code"] == 200
    assert res["gpu_count"] == 2
    assert res["vram_allocated_gb"] == 160
    assert res["security_context"] == "NON_ROOT_USER"

def test_readiness_probe_missing_gpu():
    v = ContainerEnvironmentValidator()
    v.simulate_build_stage("runner", [])
    res = v.verify_readiness_probe()
    assert res["status"] == "NOT_READY"
    assert res["http_code"] == 503
    assert res["reason"] == "NO_GPU_DEVICES_DETECTED"

def test_readiness_probe_running_as_root_fails():
    v = ContainerEnvironmentValidator()
    v.configure_gpu_devices(["/dev/nvidia0"])
    v.is_running_as_non_root = False  # Root user
    
    res = v.verify_readiness_probe()
    assert res["status"] == "SECURITY_WARNING"
    assert res["http_code"] == 500
    assert res["reason"] == "RUNNING_AS_ROOT"

def test_single_gpu_vram_calculation():
    v = ContainerEnvironmentValidator()
    v.simulate_build_stage("runner", [])
    v.configure_gpu_devices(["/dev/nvidia0"], vram_per_device_gb=24)
    res = v.verify_readiness_probe()
    assert res["vram_allocated_gb"] == 24
