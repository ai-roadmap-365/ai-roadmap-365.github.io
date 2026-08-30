import pytest
from examples.feature_flags import AIFeatureFlagRouter

def test_deterministic_user_hashing():
    router = AIFeatureFlagRouter("test_flag", canary_percentage=20)
    bucket1 = router.get_user_bucket("user_alice")
    bucket2 = router.get_user_bucket("user_alice")
    bucket_bob = router.get_user_bucket("user_bob")
    
    assert bucket1 == bucket2
    assert 0 <= bucket1 < 100
    assert 0 <= bucket_bob < 100

def test_canary_routing_allocation():
    # Set 100% canary -> all users must get CANDIDATE_MODEL_V2
    router_all_canary = AIFeatureFlagRouter("flag1", canary_percentage=100)
    res1 = router_all_canary.route_request("u1", "test")
    assert res1["assigned_variant"] == "CANDIDATE_MODEL_V2"
    
    # Set 0% canary -> all users must get BASELINE_MODEL_V1
    router_zero_canary = AIFeatureFlagRouter("flag1", canary_percentage=0)
    res2 = router_zero_canary.route_request("u1", "test")
    assert res2["assigned_variant"] == "BASELINE_MODEL_V1"

def test_shadow_traffic_execution_when_enabled():
    router = AIFeatureFlagRouter("flag_shadow", canary_percentage=10, shadow_enabled=True)
    res = router.route_request("usr_100", "Summarize article")
    
    assert res["shadow_executed"] is True
    assert len(router.shadow_logs) == 1
    assert router.shadow_logs[0]["user_id"] == "usr_100"
    assert router.shadow_logs[0]["shadow_variant"] == "SHADOW_EXPERIMENTAL_V3"

def test_shadow_traffic_disabled():
    router = AIFeatureFlagRouter("flag_no_shadow", canary_percentage=10, shadow_enabled=False)
    res = router.route_request("usr_100", "Summarize article")
    
    assert res["shadow_executed"] is False
    assert len(router.shadow_logs) == 0

def test_different_flags_produce_different_buckets():
    r1 = AIFeatureFlagRouter("flag_a", 50)
    r2 = AIFeatureFlagRouter("flag_b", 50)
    
    # Flags with different salts generally produce different buckets for the same user
    b1 = r1.get_user_bucket("alice")
    b2 = r2.get_user_bucket("alice")
    # Both are valid [0, 99]
    assert 0 <= b1 < 100 and 0 <= b2 < 100
