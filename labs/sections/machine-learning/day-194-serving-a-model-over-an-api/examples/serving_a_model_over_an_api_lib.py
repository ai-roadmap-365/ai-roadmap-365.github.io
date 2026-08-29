import time
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SingleFeatureInput:
    tenure_months: float
    monthly_spend: float
    support_tickets: int

@dataclass
class ServiceHealthStatus:
    is_live: bool
    is_ready: bool
    model_version: str

class ModelServingEngine:
    def __init__(self, model_version: str = "v1.2.0"):
        self.model_version = model_version
        self._is_ready = False
        self._weights = None
        self._bias = 0.0

    def load_model(self, weights: np.ndarray, bias: float) -> None:
        self._weights = np.array(weights, dtype=float)
        self._bias = float(bias)
        self._is_ready = True

    def health_check(self) -> ServiceHealthStatus:
        return ServiceHealthStatus(
            is_live=True,
            is_ready=self._is_ready,
            model_version=self.model_version if self._is_ready else "UNLOADED"
        )

    def _fallback_heuristic(self, features: np.ndarray) -> float:
        spend = features[1]
        tickets = features[2]
        if tickets >= 3 or spend > 150.0:
            return 0.75
        return 0.20

    def predict_single(self, input_data: SingleFeatureInput) -> Dict[str, Any]:
        t0 = time.perf_counter()
        if not self._is_ready:
            raise RuntimeError("Model is not loaded. Service unavailable.")

        if input_data.tenure_months < 0 or input_data.monthly_spend < 0:
            raise ValueError("Feature values cannot be negative")

        features = np.array([
            input_data.tenure_months,
            input_data.monthly_spend,
            float(input_data.support_tickets)
        ])

        try:
            z = float(np.dot(self._weights, features) + self._bias)
            prob = 1.0 / (1.0 + np.exp(-z))
            used_fallback = False
        except Exception:
            prob = self._fallback_heuristic(features)
            used_fallback = True

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "churn_probability": round(float(prob), 4),
            "prediction": 1 if prob >= 0.5 else 0,
            "used_fallback": used_fallback,
            "model_version": self.model_version,
            "latency_ms": round(latency_ms, 3)
        }

    def predict_batch(self, batch_data: List[SingleFeatureInput]) -> List[Dict[str, Any]]:
        return [self.predict_single(item) for item in batch_data]

def run_serving_demo():
    engine = ModelServingEngine()
    engine.load_model(weights=np.array([0.02, 0.015, 0.40]), bias=-1.5)
    sample = SingleFeatureInput(tenure_months=12.0, monthly_spend=85.0, support_tickets=2)
    res = engine.predict_single(sample)
    print(f"Serving Demo: Churn Probability = {res['churn_probability']}, Latency = {res['latency_ms']}ms")
    return engine, res

if __name__ == "__main__":
    run_serving_demo()
