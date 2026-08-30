import math
import numpy as np
from typing import Tuple, Dict, Any

class ELOEvaluator:
    def __init__(self, initial_elo: float = 1000.0, k_factor: float = 32.0):
        self.ratings: Dict[str, float] = {}
        self.initial_elo = initial_elo
        self.k = k_factor

    def get_rating(self, model: str) -> float:
        return self.ratings.get(model, self.initial_elo)

    def compute_expected_score(self, r_a: float, r_b: float) -> float:
        return 1.0 / (1.0 + 10.0 ** ((r_b - r_a) / 400.0))

    def update_match(self, model_a: str, model_b: str, score_a: float) -> Tuple[float, float]:
        r_a = self.get_rating(model_a)
        r_b = self.get_rating(model_b)

        e_a = self.compute_expected_score(r_a, r_b)
        e_b = 1.0 - e_a

        new_r_a = r_a + self.k * (score_a - e_a)
        new_r_b = r_b + self.k * ((1.0 - score_a) - e_b)

        self.ratings[model_a] = round(new_r_a, 2)
        self.ratings[model_b] = round(new_r_b, 2)
        return self.ratings[model_a], self.ratings[model_b]

def compute_pass_at_k(n: int, c: int, k: int) -> float:
    # 1 - comb(n - c, k) / comb(n, k)
    if n - c < k:
        return 1.0
    
    prod = 1.0
    for i in range(k):
        prod *= (n - c - i) / (n - i)
    return round(1.0 - prod, 4)

def run_benchmarking_demo():
    evaluator = ELOEvaluator()
    r_a, r_b = evaluator.update_match("Claude-3.5", "GPT-4o", 1.0) # Claude wins
    
    # 10 samples, 4 correct, pass@1 and pass@3
    p1 = compute_pass_at_k(10, 4, 1)
    p3 = compute_pass_at_k(10, 4, 3)

    print(f"Benchmarking Demo: ELO A = {r_a}, ELO B = {r_b}, pass@1 = {p1*100}%, pass@3 = {p3*100}%")
    return r_a, r_b, p1, p3

if __name__ == "__main__":
    run_benchmarking_demo()
