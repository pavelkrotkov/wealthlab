"""Unrelated short-index liabilities and rejected exits cannot inherit a protected-stock floor."""

from tests.option_market_cases import change, flat, shocked
from wealthlab.markets.household_run import run


def test_short_index_loss_can_exceed_capital_and_survives_as_actual_household_liability():
    scenario, batch, binding = shocked("Four-leg synthetic exposure", "index", -0.8)

    def setup(data):
        case = data["option_plan"]["case"]
        case.update(cash_secure_puts=False, short_collateral_fraction="0")
        next(leg for leg in case["legs"] if leg["id"] == "index_put")["contracts"] = 20

    result = run(change(scenario, setup), batch, binding)
    final = result["details"][0]["rows"][-1]
    assert final["option_liability"] > 0
    assert final["net_wealth"] < 0
    assert result["outcomes"][0]["option_negative_equity_months"] > 0
    assert not result["outcomes"][0]["joint_feasible"]


def test_rejected_terminal_stock_sale_preserves_marked_shares_and_reports_incomplete_exit():
    scenario, batch, binding = flat("Covered call")
    scenario = change(
        scenario, lambda data: data["option_plan"]["case"].update(stock_sale_fee="20000")
    )
    result = run(scenario, batch, binding)
    final = result["details"][0]["rows"][-1]
    assert final["option_shares"] == 100
    assert result["outcomes"][0]["option_exit_blocked_months"] == 1
    assert result["outcomes"][0]["first_product_failure"] == "2026-12-31"
    assert not result["outcomes"][0]["product_feasible"]
