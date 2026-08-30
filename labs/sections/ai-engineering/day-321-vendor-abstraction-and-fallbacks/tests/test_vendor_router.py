import pytest
from examples.vendor_router import VendorFallbackRouter

def test_primary_provider_success():
    router = VendorFallbackRouter()
    res = router.call_model_with_fallback("Write a poem")
    assert res["status"] == "SUCCESS"
    assert res["resolved_provider"] == "anthropic"
    assert res["fallback_occurred"] is False
    assert res["attempted_providers"] == ["anthropic"]

def test_secondary_failover_when_primary_fails():
    router = VendorFallbackRouter()
    res = router.call_model_with_fallback("Write a poem", simulated_failing_providers=["anthropic"])
    assert res["status"] == "SUCCESS"
    assert res["resolved_provider"] == "openai"
    assert res["fallback_occurred"] is True
    assert res["attempted_providers"] == ["anthropic", "openai"]

def test_tertiary_fallback_when_top_two_fail():
    router = VendorFallbackRouter()
    res = router.call_model_with_fallback("Write a poem", simulated_failing_providers=["anthropic", "openai"])
    assert res["status"] == "SUCCESS"
    assert res["resolved_provider"] == "vllm_local"
    assert res["fallback_occurred"] is True
    assert len(res["attempted_providers"]) == 3

def test_all_providers_failed():
    router = VendorFallbackRouter()
    res = router.call_model_with_fallback("Write a poem", simulated_failing_providers=["anthropic", "openai", "vllm_local"])
    assert res["status"] == "ALL_PROVIDERS_FAILED"
    assert "503" in res["error"]

def test_unhealthy_provider_flag():
    router = VendorFallbackRouter()
    router.set_provider_health("anthropic", False)
    res = router.call_model_with_fallback("Write a poem")
    assert res["status"] == "SUCCESS"
    assert res["resolved_provider"] == "openai"
    assert res["fallback_occurred"] is True
