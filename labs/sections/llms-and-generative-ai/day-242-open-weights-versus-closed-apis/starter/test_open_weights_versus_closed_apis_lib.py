import pytest
from examples.open_weights_versus_closed_apis_lib import TCOCalculator

def test_break_even_calculation():
    # 8x H100 node: $24/hr * 720 = $17,280 + $5,000 MLOps = $22,280 / mo
    # API: $3.00 / M -> $22,280 / 0.000003 = 7,426,666,667 tokens / mo
    # Daily: ~247,555,555 tokens / day (~247.56M)
    calc = TCOCalculator(gpu_hourly_cost=24.0, mlops_monthly_cost=5000.0)
    be = calc.calculate_break_even(3.00)
    assert be == pytest.approx(247555555.56, rel=1e-3)

def test_decision_evaluation():
    calc = TCOCalculator(gpu_hourly_cost=24.0, mlops_monthly_cost=5000.0)
    
    # 10M daily -> API is vastly cheaper ($900 vs $22,280)
    assert calc.evaluate_decision(10.0, 3.00) == "Closed API"

    # 500M daily -> Self-hosting is vastly cheaper ($45,000 vs $22,280)
    assert calc.evaluate_decision(500.0, 3.00) == "Self-Hosted"

def test_zero_mlops_cost_break_even():
    calc = TCOCalculator(gpu_hourly_cost=10.0, mlops_monthly_cost=0.0)
    # Fixed = $7,200/mo. API = $2.00/M. Monthly tokens = 3.6B -> Daily = 120M
    be = calc.calculate_break_even(2.00)
    assert be == pytest.approx(120000000.0, rel=1e-3)
