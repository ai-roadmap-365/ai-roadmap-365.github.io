import pytest
import numpy as np
from examples.section_project_an_ml_service_lib import (
    CustomerFeatures, ProductionModelRegistry, DeployedMLService
)

def test_deployed_ml_service_lifecycle():
    reg = ProductionModelRegistry()
    reg.register_and_promote("churn_model", "v1.0", np.array([0.02, 0.01, 0.5]), -1.0, 0.85)

    service = DeployedMLService(reg, "churn_model")
    sample = CustomerFeatures(tenure_months=12.0, monthly_spend=100.0, support_tickets=1)
    res = service.predict(sample)

    assert "churn_probability" in res
    assert 0.0 <= res["churn_probability"] <= 1.0
    assert res["model_version"] == "v1.0"
    assert res["used_fallback"] is False

def test_deployed_ml_service_drift_detection():
    np.random.seed(42)
    reg = ProductionModelRegistry()
    reg.register_and_promote("churn_model", "v1.0", np.array([0.02, 0.01, 0.5]), -1.0, 0.85)

    service = DeployedMLService(reg, "churn_model")
    ref = np.random.normal(50.0, 10.0, 1000)
    service.set_reference_data(ref)

    # Shifted data
    drifted = np.random.normal(80.0, 20.0, 1000)
    psi, status = service.evaluate_feature_drift_psi(drifted)

    assert psi >= 0.20
    assert status == "SIGNIFICANT_DRIFT"
