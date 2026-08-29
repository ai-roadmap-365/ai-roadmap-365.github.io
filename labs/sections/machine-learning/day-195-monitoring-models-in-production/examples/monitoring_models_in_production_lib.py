import numpy as np
from typing import Tuple, Dict, Any

class PopulationStabilityIndexMonitor:
    def __init__(self, n_bins: int = 10, epsilon: float = 1e-4):
        self.n_bins = n_bins
        self.epsilon = epsilon

    def compute_bin_boundaries(self, reference: np.ndarray) -> np.ndarray:
        quantiles = np.linspace(0, 100, self.n_bins + 1)
        bin_edges = np.percentile(reference, quantiles)
        bin_edges[0] = -np.inf
        bin_edges[-1] = np.inf
        return bin_edges

    def calculate_psi(self, reference: np.ndarray, current: np.ndarray) -> Tuple[float, Dict[str, Any]]:
        bin_edges = self.compute_bin_boundaries(reference)

        ref_counts, _ = np.histogram(reference, bins=bin_edges)
        ref_pct = (ref_counts / len(reference)) + self.epsilon

        cur_counts, _ = np.histogram(current, bins=bin_edges)
        cur_pct = (cur_counts / len(current)) + self.epsilon

        ref_pct = ref_pct / np.sum(ref_pct)
        cur_pct = cur_pct / np.sum(cur_pct)

        psi_terms = (cur_pct - ref_pct) * np.log(cur_pct / ref_pct)
        total_psi = float(np.sum(psi_terms))

        if total_psi < 0.10:
            status = "STABLE"
        elif total_psi < 0.20:
            status = "MODERATE_DRIFT"
        else:
            status = "SIGNIFICANT_DRIFT"

        details = {
            "psi": round(total_psi, 4),
            "status": status
        }
        return total_psi, details

def run_monitoring_demo():
    np.random.seed(42)
    ref = np.random.normal(50.0, 10.0, 1000)
    stable = np.random.normal(50.2, 10.1, 1000)
    drifted = np.random.normal(62.0, 14.0, 1000)

    monitor = PopulationStabilityIndexMonitor()
    psi_stable, det_stable = monitor.calculate_psi(ref, stable)
    psi_drift, det_drift = monitor.calculate_psi(ref, drifted)

    print(f"Monitoring Demo: Stable PSI = {det_stable['psi']} ({det_stable['status']}), Drifted PSI = {det_drift['psi']} ({det_drift['status']})")
    return monitor, det_stable, det_drift

if __name__ == "__main__":
    run_monitoring_demo()
