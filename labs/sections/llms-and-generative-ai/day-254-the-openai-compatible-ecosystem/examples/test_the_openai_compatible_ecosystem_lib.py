import pytest
from examples.the_openai_compatible_ecosystem_lib import (
    MultiProviderRouter,
    ProviderConfig
)

def test_router_priority_order():
    router = MultiProviderRouter()
    router.register_provider(ProviderConfig("Cloud_Tier2", "https://api.cloud.com/v1", "k2", "m2", priority=2))
    router.register_provider(ProviderConfig("Local_Tier1", "http://localhost:8000/v1", "k1", "m1", priority=1))

    resp = router.dispatch_completion([{"role": "user", "content": "Test"}])
    assert resp["routed_provider"] == "Local_Tier1"
    assert resp["choices"][0]["message"]["content"] == "Routed response success."

def test_automated_failover():
    router = MultiProviderRouter()
    # Primary fails, fallback succeeds
    router.register_provider(ProviderConfig("Failing_Primary", "http://bad:8000/v1", "k1", "m1", priority=1))
    router.register_provider(ProviderConfig("Healthy_Backup", "https://api.good.com/v1", "k2", "m2", priority=2))

    resp = router.dispatch_completion([{"role": "user", "content": "Test"}])
    assert resp["routed_provider"] == "Healthy_Backup"

def test_all_providers_failing_raises_runtime_error():
    router = MultiProviderRouter()
    router.register_provider(ProviderConfig("Failing_1", "http://bad1/v1", "k1", "m1", priority=1))
    router.register_provider(ProviderConfig("Failing_2", "http://bad2/v1", "k2", "m2", priority=2))

    with pytest.raises(RuntimeError) as exc_info:
        router.dispatch_completion([{"role": "user", "content": "Test"}])
    assert "All 2 providers failed" in str(exc_info.value)

def test_empty_router_raises_value_error():
    router = MultiProviderRouter()
    with pytest.raises(ValueError):
        router.dispatch_completion([{"role": "user", "content": "Test"}])
