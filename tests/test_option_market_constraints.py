"""Funding and product constraints remain distinct.

A protective stock put cannot fund unrelated index margin or erase an earlier
required collateral failure after prices subsequently fall.
"""

from tests.option_market_cases import change, shocked
from wealthlab.markets.household_run import run


def test_index_loss_and_collateral_can_fail_spending_despite_a_stock_protective_put():
    scenario, batch, binding = shocked("Four-leg synthetic exposure", "index", -0.8)
    result = run(scenario, batch, binding)
    outcome = result["outcomes"][0]
    assert outcome["funding_shortfall"] > 0
    assert outcome["ending_nominal_wealth"] < 24200
    assert not outcome["joint_feasible"]
    assert result["details"][0]["rows"][-1]["option_shares"] == 0


def test_opening_margin_failure_is_not_erased_by_later_price_recovery_or_ending_cash():
    scenario, batch, binding = shocked("Covered call", "stock", -0.9)

    def setup(data):
        data["accounts"][0]["balance"] = "1000"
        data["expenses"] = []
        data["option_plan"]["case"]["cover_stock_calls"] = False

    scenario = change(scenario, setup)
    result = run(scenario, batch, binding)
    outcome = result["outcomes"][0]
    assert result["details"][0]["rows"][0]["option_margin_unfunded"] == 0
    assert outcome["funded"]
    assert outcome["option_margin_failure_months"] == 1
    assert outcome["first_product_failure"] == "2026-01-01"
    assert not outcome["joint_feasible"]
