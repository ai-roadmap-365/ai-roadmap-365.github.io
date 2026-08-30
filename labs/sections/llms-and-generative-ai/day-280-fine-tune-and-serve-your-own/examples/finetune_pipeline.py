# End-to-End Fine-Tuning, Merging, Serving, and Evaluation Pipeline
import numpy as np
import json
from typing import Dict, List, Any, Tuple, Optional

class LoRAWeightMerger:
    """Performs exact mathematical merging of LoRA adapters into base model weights."""

    @staticmethod
    def merge_weights(base_w: np.ndarray, lora_a: np.ndarray, lora_b: np.ndarray, r: int, alpha: float) -> np.ndarray:
        """
        Merges W_merged = W_base + (B @ A) * (alpha / r)
        base_w: (d_out, d_in)
        lora_a: (r, d_in)
        lora_b: (d_out, r)
        """
        if r <= 0:
            raise ValueError("LoRA rank r must be > 0")
        
        scaling = float(alpha) / float(r)
        delta_w = np.matmul(lora_b, lora_a) * scaling
        
        if delta_w.shape != base_w.shape:
            raise ValueError(f"Shape mismatch: delta_w {delta_w.shape} vs base_w {base_w.shape}")

        return (base_w + delta_w).astype(np.float32)

class MockModelServer:
    """Simulates local OpenAI-compatible inference server."""

    def __init__(self, is_finetuned: bool = True):
        self.is_finetuned = is_finetuned

    def generate_completion(self, prompt: str) -> str:
        """Simulates generation based on model type."""
        if "sql" in prompt.lower() or "query" in prompt.lower():
            if self.is_finetuned:
                return '```sql\nSELECT id, username, email FROM users WHERE active = 1;\n```'
            else:
                return 'Sure! Here is some information about users: You can write a query like SELECT * FROM users probably.'
        elif "json" in prompt.lower() or "schema" in prompt.lower():
            if self.is_finetuned:
                return '{"status": "success", "user_id": 1042, "role": "admin"}'
            else:
                return 'Here is your JSON output: status: success, user_id: 1042 (Note: this is not valid JSON)'
        else:
            return "Standard response."

class ModelEvaluationBenchmark:
    """Automated benchmark evaluating schema compliance and exact match accuracy."""

    @staticmethod
    def evaluate_json_compliance(predictions: List[str]) -> float:
        """Measures percentage of predictions that are valid JSON."""
        if not predictions:
            return 0.0
        valid_count = 0
        for pred in predictions:
            try:
                json.loads(pred.strip())
                valid_count += 1
            except Exception:
                pass
        return (valid_count / len(predictions)) * 100.0

    @staticmethod
    def evaluate_exact_match(predictions: List[str], targets: List[str]) -> float:
        """Measures percentage of exact match against golden targets."""
        if not predictions or len(predictions) != len(targets):
            return 0.0
        matches = sum(1 for p, t in zip(predictions, targets) if p.strip() == t.strip())
        return (matches / len(predictions)) * 100.0

    @staticmethod
    def run_benchmark_comparison(base_server: MockModelServer, ft_server: MockModelServer, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """Compares base model vs fine-tuned model on test cases."""
        prompts = [tc["prompt"] for tc in test_cases]
        targets = [tc["target"] for tc in test_cases]

        base_preds = [base_server.generate_completion(p) for p in prompts]
        ft_preds = [ft_server.generate_completion(p) for p in prompts]

        base_json_rate = ModelEvaluationBenchmark.evaluate_json_compliance(base_preds)
        ft_json_rate = ModelEvaluationBenchmark.evaluate_json_compliance(ft_preds)

        base_em = ModelEvaluationBenchmark.evaluate_exact_match(base_preds, targets)
        ft_em = ModelEvaluationBenchmark.evaluate_exact_match(ft_preds, targets)

        return {
            "total_cases": len(test_cases),
            "base_json_compliance": base_json_rate,
            "finetuned_json_compliance": ft_json_rate,
            "base_exact_match": base_em,
            "finetuned_exact_match": ft_em,
            "accuracy_improvement": ft_em - base_em
        }
