import numpy as np
import time
from typing import Dict, Any, List, Optional

class AIObservabilityAlertEngine:
    def __init__(self, p95_ttft_threshold_ms: float = 300.0, error_rate_threshold_pct: float = 1.0):
        self.ttft_threshold = float(p95_ttft_threshold_ms)
        self.error_threshold = float(error_rate_threshold_pct)
        self.ttft_samples: List[float] = []
        self.total_requests = 0
        self.total_errors = 0
        self.active_alerts: List[Dict[str, Any]] = []

    def record_inference_event(self, ttft_ms: float, is_error: bool = False):
        self.total_requests += 1
        if is_error:
            self.total_errors += 1
        else:
            self.ttft_samples.append(float(ttft_ms))

    def evaluate_metrics(self) -> Dict[str, Any]:
        if not self.ttft_samples:
            p50 = p95 = p99 = 0.0
        else:
            p50 = float(np.percentile(self.ttft_samples, 50))
            p95 = float(np.percentile(self.ttft_samples, 95))
            p99 = float(np.percentile(self.ttft_samples, 99))

        error_rate = (self.total_errors / self.total_requests * 100.0) if self.total_requests > 0 else 0.0

        self.active_alerts.clear()
        if p95 > self.ttft_threshold:
            self.active_alerts.append({
                "severity": "CRITICAL",
                "alert_name": "HighTailLatencyP95",
                "message": f"P95 TTFT ({round(p95, 1)}ms) exceeded threshold ({self.ttft_threshold}ms)",
                "timestamp": time.time()
            })

        if error_rate > self.error_threshold:
            self.active_alerts.append({
                "severity": "CRITICAL",
                "alert_name": "HighInferenceErrorRate",
                "message": f"Error rate ({round(error_rate, 2)}%) exceeded threshold ({self.error_threshold}%)",
                "timestamp": time.time()
            })

        return {
            "total_requests": self.total_requests,
            "p50_ttft_ms": round(p50, 2),
            "p95_ttft_ms": round(p95, 2),
            "p99_ttft_ms": round(p99, 2),
            "error_rate_pct": round(error_rate, 2),
            "active_alert_count": len(self.active_alerts)
        }

if __name__ == "__main__":
    e = AIObservabilityAlertEngine()
    e.record_inference_event(100.0)
    print(e.evaluate_metrics())
