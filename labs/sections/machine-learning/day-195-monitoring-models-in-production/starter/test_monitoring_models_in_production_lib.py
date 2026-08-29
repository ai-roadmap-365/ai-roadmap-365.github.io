import pytest
import numpy as np
from examples.monitoring_models_in_production_lib import PopulationStabilityIndexMonitor

def test_psi_identical_distributions_is_near_zero():
    np.random.seed(42)
    ref = np.random.normal(100.0, 15.0, 2000)
    cur = np.random.normal(100.0, 15.0, 2000)

    monitor = PopulationStabilityIndexMonitor()
    psi, details = monitor.calculate_psi(ref, cur)

    assert psi < 0.05
    assert details["status"] == "STABLE"

def test_psi_shifted_distribution_detects_significant_drift():
    np.random.seed(42)
    ref = np.random.normal(100.0, 15.0, 2000)
    # Severe shift: mean from 100 to 140
    cur = np.random.normal(140.0, 20.0, 2000)

    monitor = PopulationStabilityIndexMonitor()
    psi, details = monitor.calculate_psi(ref, cur)

    assert psi >= 0.20
    assert details["status"] == "SIGNIFICANT_DRIFT"
