from typing import Dict, Any, Tuple

class ModelRouter:
    def __init__(self):
        # Pricing per 1M tokens: (input_price, output_price)
        self.pricing = {
            "claude-3.5-sonnet": (3.00, 15.00),
            "gpt-4o": (2.50, 10.00),
            "gemini-2.0-flash": (0.10, 0.40),
            "gpt-4o-mini": (0.15, 0.60)
        }

    def route_query(self, prompt: str, token_count: int = 100) -> str:
        prompt_lower = prompt.lower()
        if token_count > 150000:
            return "gemini-2.0-flash"

        if "def " in prompt or "class " in prompt or "theorem" in prompt_lower or "refactor" in prompt_lower:
            return "claude-3.5-sonnet"

        if token_count < 300 and ("classify" in prompt_lower or "extract" in prompt_lower or "sentiment" in prompt_lower):
            return "gpt-4o-mini"

        return "gemini-2.0-flash"

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int, is_cached: bool = False) -> float:
        in_rate, out_rate = self.pricing.get(model, (1.0, 3.0))
        if is_cached:
            in_rate = in_rate * 0.25 # 75% prompt cache discount

        cost = (input_tokens / 1e6) * in_rate + (output_tokens / 1e6) * out_rate
        return round(cost, 6)

def run_routing_demo():
    router = ModelRouter()
    m1 = router.route_query("def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)")
    m2 = router.route_query("Classify the sentiment of this review", token_count=50)
    m3 = router.route_query("Analyze complete archive", token_count=500000)

    cost_sonnet = router.calculate_cost("claude-3.5-sonnet", input_tokens=50000, output_tokens=1000)
    cost_cached = router.calculate_cost("claude-3.5-sonnet", input_tokens=50000, output_tokens=1000, is_cached=True)

    print(f"Router Demo: Code -> {m1}, Quick -> {m2}, Long -> {m3}, Sonnet Cost = ${cost_sonnet:.4f}, Cached = ${cost_cached:.4f}")
    return m1, m2, m3, cost_sonnet, cost_cached

if __name__ == "__main__":
    run_routing_demo()
