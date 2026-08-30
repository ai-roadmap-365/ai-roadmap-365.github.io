import pytest
from examples.cloud_deployment import CloudDeploymentOrchestrator

def test_initial_deployment_state():
    orchestrator = CloudDeploymentOrchestrator()
    assert orchestrator.active_environment == "BLUE"
    assert orchestrator.revisions["BLUE"]["active_traffic_pct"] == 100
    assert orchestrator.revisions["GREEN"]["active_traffic_pct"] == 0

def test_successful_blue_to_green_cutover():
    orchestrator = CloudDeploymentOrchestrator()
    res = orchestrator.deploy_new_revision("v2.0.0", simulate_health_pass=True)
    
    assert res["status"] == "DEPLOYMENT_SUCCESS"
    assert orchestrator.active_environment == "GREEN"
    assert orchestrator.revisions["GREEN"]["image_tag"] == "v2.0.0"
    assert orchestrator.revisions["GREEN"]["active_traffic_pct"] == 100
    assert orchestrator.revisions["BLUE"]["active_traffic_pct"] == 0

def test_subsequent_green_to_blue_cutover():
    orchestrator = CloudDeploymentOrchestrator()
    orchestrator.deploy_new_revision("v2.0.0", simulate_health_pass=True) # Now GREEN
    
    res = orchestrator.deploy_new_revision("v3.0.0", simulate_health_pass=True) # Back to BLUE
    assert res["status"] == "DEPLOYMENT_SUCCESS"
    assert orchestrator.active_environment == "BLUE"
    assert orchestrator.revisions["BLUE"]["image_tag"] == "v3.0.0"
    assert orchestrator.revisions["BLUE"]["active_traffic_pct"] == 100
    assert orchestrator.revisions["GREEN"]["active_traffic_pct"] == 0

def test_failed_health_check_aborts_cutover():
    orchestrator = CloudDeploymentOrchestrator()
    # Attempt deployment to GREEN that fails health probe
    res = orchestrator.deploy_new_revision("v2.0.0-buggy", simulate_health_pass=False)
    
    assert res["status"] == "DEPLOYMENT_FAILED_HEALTH_CHECK"
    assert orchestrator.active_environment == "BLUE" # Preserves BLUE
    assert orchestrator.revisions["BLUE"]["active_traffic_pct"] == 100
    assert orchestrator.revisions["GREEN"]["active_traffic_pct"] == 0
    assert orchestrator.revisions["GREEN"]["healthy"] is False

def test_deployment_history_logging():
    orchestrator = CloudDeploymentOrchestrator()
    orchestrator.deploy_new_revision("v2.0.0", True)
    orchestrator.deploy_new_revision("v2.1.0-bad", False)
    
    assert len(orchestrator.deployment_history) == 2
    assert orchestrator.deployment_history[0]["status"] == "DEPLOYMENT_SUCCESS"
    assert orchestrator.deployment_history[1]["status"] == "DEPLOYMENT_FAILED_HEALTH_CHECK"
