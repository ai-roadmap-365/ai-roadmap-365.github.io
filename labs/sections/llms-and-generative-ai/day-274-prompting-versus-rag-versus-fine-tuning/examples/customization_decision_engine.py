# Customization Strategy Decision Engine
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class ProjectRequirements:
    task_complexity: float        # 0.0 to 1.0
    knowledge_dynamism: float     # 0.0 (static) to 1.0 (hourly/real-time)
    strict_style_adherence: float # 0.0 (generic prose) to 1.0 (exact DSL/JSON syntax)
    data_privacy_budget: float    # 0.0 (public cloud API) to 1.0 (air-gapped)
    inference_latency_sla_ms: int # Max allowable P95 latency in ms
    labeled_data_volume: int      # Count of verified training pairs
    monthly_request_volume: int   # Anticipated monthly query volume
    monthly_budget_usd: float     # Maximum allowable monthly spend

class CustomizationStrategyEngine:
    """Evaluates engineering requirements and recommends customization paradigms."""

    def __init__(self):
        self.strategies = ["Prompting_FewShot", "RAG_Hybrid", "PEFT_LoRA", "Full_FineTuning"]

    def evaluate_strategy(self, req: ProjectRequirements) -> Dict[str, Any]:
        scores: Dict[str, float] = {}

        # 1. Prompting Score
        p_score = 100.0
        if req.task_complexity > 0.75: p_score -= 25.0
        if req.knowledge_dynamism > 0.8: p_score -= 15.0
        if req.strict_style_adherence > 0.8: p_score -= 30.0
        if req.inference_latency_sla_ms < 300: p_score -= 20.0
        if req.monthly_request_volume > 500000: p_score -= 25.0
        scores["Prompting_FewShot"] = max(0.0, min(100.0, p_score))

        # 2. RAG Score
        r_score = 40.0
        r_score += req.knowledge_dynamism * 45.0
        if req.task_complexity > 0.4: r_score += 20.0
        if req.strict_style_adherence > 0.85: r_score -= 15.0
        if req.inference_latency_sla_ms < 150: r_score -= 25.0
        scores["RAG_Hybrid"] = max(0.0, min(100.0, r_score))

        # 3. PEFT / LoRA Score
        l_score = 35.0
        l_score += req.strict_style_adherence * 35.0
        if req.labeled_data_volume >= 500: l_score += 25.0
        elif req.labeled_data_volume < 100: l_score -= 30.0
        if req.knowledge_dynamism > 0.6: l_score -= 30.0
        if req.inference_latency_sla_ms < 200: l_score += 15.0
        if req.monthly_request_volume > 100000: l_score += 15.0
        scores["PEFT_LoRA"] = max(0.0, min(100.0, l_score))

        # 4. Full Fine-Tuning
        f_score = 10.0
        if req.labeled_data_volume >= 50000: f_score += 40.0
        else: f_score -= 40.0
        if req.monthly_budget_usd < 2000.0: f_score -= 40.0
        if req.strict_style_adherence > 0.9: f_score += 20.0
        scores["Full_FineTuning"] = max(0.0, min(100.0, f_score))

        best_strategy = max(scores, key=lambda k: scores[k])

        return {
            "recommended_strategy": best_strategy,
            "scores": scores,
            "reasoning": self._generate_reasoning(best_strategy, req)
        }

    def calculate_cost_break_even(
        self,
        prompt_tokens_per_req: int,
        completion_tokens_per_req: int,
        prompting_cost_per_m: float,
        fine_tuned_cost_per_m: float,
        fine_tuning_setup_cost_usd: float
    ) -> Dict[str, float]:
        """Computes monthly break-even request volume between Prompting and Fine-Tuning."""
        prompting_req_cost = ((prompt_tokens_per_req + completion_tokens_per_req) / 1_000_000.0) * prompting_cost_per_m
        
        # Fine-tuned models use minimal prompt overhead (e.g. 10% of prompt tokens)
        ft_prompt_tokens = max(50, int(prompt_tokens_per_req * 0.15))
        fine_tuned_req_cost = ((ft_prompt_tokens + completion_tokens_per_req) / 1_000_000.0) * fine_tuned_cost_per_m
        
        cost_diff_per_req = prompting_req_cost - fine_tuned_req_cost
        
        if cost_diff_per_req <= 0:
            break_even_requests = float('inf')
        else:
            break_even_requests = fine_tuning_setup_cost_usd / cost_diff_per_req

        return {
            "prompting_cost_per_request": prompting_req_cost,
            "fine_tuned_cost_per_request": fine_tuned_req_cost,
            "savings_per_request": max(0.0, cost_diff_per_req),
            "break_even_requests": break_even_requests
        }

    def _generate_reasoning(self, strategy: str, req: ProjectRequirements) -> str:
        if strategy == "RAG_Hybrid":
            return f"High knowledge dynamism ({req.knowledge_dynamism:.2f}) and factual grounding requirements mandate external retrieval."
        elif strategy == "PEFT_LoRA":
            return f"High style/syntax requirement ({req.strict_style_adherence:.2f}) with {req.labeled_data_volume} samples favors parameter-efficient adaptation."
        elif strategy == "Prompting_FewShot":
            return "Task complexity is manageable via in-context learning with zero upfront training overhead."
        else:
            return f"Massive labeled dataset ({req.labeled_data_volume}) and distinct domain warrants foundational weight adaptation."
