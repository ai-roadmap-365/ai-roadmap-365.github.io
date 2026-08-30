from typing import Dict, Any

class TCOCalculator:
    def __init__(self, gpu_hourly_cost: float = 24.0, mlops_monthly_cost: float = 5000.0):
        self.gpu_hourly_cost = gpu_hourly_cost
        self.mlops_monthly_cost = mlops_monthly_cost

    def calculate_break_even(self, api_rate_per_million: float) -> float:
        fixed_monthly = (self.gpu_hourly_cost * 24 * 30) + self.mlops_monthly_cost
        monthly_tokens = (fixed_monthly / api_rate_per_million) * 1e6
        daily_tokens = monthly_tokens / 30.0
        return round(daily_tokens, 2)

    def evaluate_decision(self, daily_tokens_millions: float, api_rate_per_million: float) -> str:
        monthly_tokens = daily_tokens_millions * 1e6 * 30
        api_monthly = (monthly_tokens / 1e6) * api_rate_per_million
        self_host_monthly = (self.gpu_hourly_cost * 24 * 30) + self.mlops_monthly_cost
        return "Self-Hosted" if self_host_monthly < api_monthly else "Closed API"

def run_tco_demo():
    calc = TCOCalculator(gpu_hourly_cost=24.0, mlops_monthly_cost=5000.0)
    be_daily = calc.calculate_break_even(3.00) # $3/M API

    dec_low = calc.evaluate_decision(10.0, 3.00) # 10M tokens/day
    dec_high = calc.evaluate_decision(500.0, 3.00) # 500M tokens/day

    print(f"TCO Demo: Break-Even = {be_daily/1e6:.2f}M Tok/Day, Low Vol = {dec_low}, High Vol = {dec_high}")
    return be_daily, dec_low, dec_high

if __name__ == "__main__":
    run_tco_demo()
