"""New unit purchases execute on the shared realized path, including real gross stock exits."""

import pytest

from tests.option_market_cases import flat
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run
from wealthlab.products.option_allocation import required_capital, scale_new_plan
from wealthlab.products.option_exit_state import from_rows
from wealthlab.products.option_purchase_example import synthetic, unit_plan


@pytest.mark.parametrize(
    "count,expected,funded,shortfall", [(1, 9499, False, 2003), (2, 19992, True, 0)]
)
def test_new_cash_units_use_actual_realized_prices_cash_and_unwind(
    count, expected, funded, shortfall
):
    _, batch, binding = flat()
    plan = scale_new_plan(unit_plan(), count, per_unit_fees_confirmed=True)
    data = synthetic().model_dump(mode="json")
    data["option_plan"] = plan.model_dump(mode="json")
    data["accounts"][1]["balance"] = str(required_capital(plan))
    result = run(Scenario.model_validate(data), batch, binding)
    rows = result["details"][0]["rows"]
    state = from_rows(rows)
    # Flat $100 stock causes the $110 call to lapse, rather than reusing the
    # dated example's $120 assignment. One unit earns $499 premium minus $3
    # buy/sale commissions. Its $3,497 early cash cannot fund $5,500 Jan-Nov
    # spending: $2,003 remains unpaid before December sale. Closing $9,499 is
    # actual cash, not proof that the household could fund all $6k spending.
    assert rows[-1]["closing_cash"] == rows[-1]["net_wealth"] == expected
    outcome = result["outcomes"][0]
    assert outcome["option_feasible"]
    assert (outcome["funded"], outcome["funding_shortfall"]) == (funded, shortfall)
    assert state["modeled_cash_exit_complete"]
    assert [(t["action"], t["quantity"]) for t in state["stock_trades"]] == [
        ("buy", str(100 * count)),
        ("sell", str(100 * count)),
    ]
    assert state["stock_trades"][-1]["id"] == "complete_unwind"
