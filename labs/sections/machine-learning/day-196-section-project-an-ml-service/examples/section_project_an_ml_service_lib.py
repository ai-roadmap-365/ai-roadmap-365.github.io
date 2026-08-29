import hashlib
import time
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple

@dataclass
class CustomerFeatures:
    tenure_months: float
    monthly_spend: float
    support_tickets: int

@dataclass
class ModelMetadata:
    model_name: str
    version: str
    sha256_hash: str
    stage: str
    weights: np.ndarray
    bias: float
    pr_auc: float

class ProductionModelRegistry:
    def __init__(self):
        self._catalog: Dict[str, Dict[str, ModelMetadata]] = {}

    def register_and_promote(
        self, name: str, version: str, weights: np.ndarray, bias: float, pr_auc: float
    ) -> ModelMetadata:
        if name not in self._catalog:
            self._catalog[name] = {}

        raw_bytes = weights.tobytes() + str(bias).encode("utf-8")
        sha256 = hashlib.sha256(raw_bytes).hexdigest()

        for meta in self._catalog[name].values():
            if meta.stage == "PRODUCTION":
                meta.stage = "ARCHIVED"

        meta = ModelMetadata(
            model_name=name, version=version, sha256_hash=sha256,
            stage="PRODUCTION", weights=weights, bias=bias, pr_auc=pr_auc
        )
        self._catalog[name][version] = meta
        return meta

    def get_production_model(self, name: str) -> Optional[ModelMetadata]:
        if name not in self._catalog:
            return None
        for meta in self._catalog[name].values():
            if meta.stage == "PRODUCTION":
                return meta
        return None

class DeployedMLService:
    def __init__(self, registry: ProductionModelRegistry, model_name: str):
        self.registry = registry
        self.model_name = model_name
        self._active_model: Optional[ModelMetadata] = None
        self.reference_spend: Optional[np.ndarray] = None
        self.load_production_model()

    def load_production_model(self) -> None:
        self._active_model = self.registry.get_production_model(self.model_name)

    def set_reference_data(self, reference_spend: np.ndarray) -> None:
        self.reference_spend = reference_spend

    def _fallback_heuristic(self, features: CustomerFeatures) -> float:
        if features.support_tickets >= 3 or features.monthly_spend > 150.0:
            return 0.75
        return 0.20

    def predict(self, sample: CustomerFeatures) -> Dict[str, Any]:
        t0 = time.perf_counter()
        if self._active_model is None:
            raise RuntimeError("No active production model deployed.")

        if sample.tenure_months < 0 or sample.monthly_spend < 0:
            raise ValueError("Feature values cannot be negative.")

        x = np.array([sample.tenure_months, sample.monthly_spend, float(sample.support_tickets)])

        try:
            z = float(np.dot(self._active_model.weights, x) + self._active_model.bias)
            prob = 1.0 / (1.0 + np.exp(-z))
            used_fallback = False
        except Exception:
            prob = self._fallback_heuristic(sample)
            used_fallback = True

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "churn_probability": round(float(prob), 4),
            "prediction": 1 if prob >= 0.5 else 0,
            "used_fallback": used_fallback,
            "model_version": self._active_model.version,
            "latency_ms": round(latency_ms, 3)
        }

    def evaluate_feature_drift_psi(self, current_spend: np.ndarray) -> Tuple[float, str]:
        if self.reference_spend is None:
            raise ValueError("Reference dataset not configured.")

        quantiles = np.linspace(0, 100, 11)
        bin_edges = np.percentile(self.reference_spend, quantiles)
        bin_edges[0] = -np.inf
        bin_edges[-1] = np.inf

        eps = 1e-4
        ref_counts, _ = np.histogram(self.reference_spend, bins=bin_edges)
        ref_pct = (ref_counts / len(self.reference_spend)) + eps
        ref_pct /= np.sum(ref_pct)

        cur_counts, _ = np.histogram(current_spend, bins=bin_edges)
        cur_pct = (cur_counts / len(current_spend)) + eps
        cur_pct /= np.sum(cur_pct)

        psi = float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))
        status = "STABLE" if psi < 0.10 else ("MODERATE_DRIFT" if psi < 0.20 else "SIGNIFICANT_DRIFT")
        return round(psi, 4), status

def run_capstone_demo():
    registry = ProductionModelRegistry()
    registry.register_and_promote(
        name="churn_service", version="v1.0.0",
        weights=np.array([0.01, 0.02, 0.45]), bias=-1.2, pr_auc=0.884
    )
    service = DeployedMLService(registry, "churn_service")
    service.set_reference_data(np.random.normal(75.0, 15.0, 1000))

    sample = CustomerFeatures(tenure_months=10.0, monthly_spend=80.0, support_tickets=2)
    pred_res = service.predict(sample)

    cur_stable = np.random.normal(75.2, 15.1, 1000)
    psi_score, drift_status = service.evaluate_feature_drift_psi(cur_stable)

    print(f"Capstone Demo: Churn Prob = {pred_res['churn_probability']}, Drift Status = {drift_status} (PSI: {psi_score})")
    return service, pred_res, psi_score

if __name__ == "__main__":
    run_capstone_demo()
