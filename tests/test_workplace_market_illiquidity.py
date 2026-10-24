"""Positive plan growth cannot replace missing wages or fund ordinary household spending."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.markets.workplace_example import synthetic


def test_locked_plan_wealth_is_neither_payroll_cash_nor_a_spending_source():
    household, market, binding = synthetic()
    data = household.model_dump(mode="json")
    data.update(incomes=[])
    data["tax_plan"]["income_rules"] = []
    data["accounts"][0]["balance"] = "0"
    data["accounts"][1]["balance"] = "100000"
    data["expenses"] = [
        dict(
            id="living",
            provenance="assumption",
            start="2026-01-01",
            end="2027-01-01",
            monthly_amount="1000",
            currency="USD",
            annual_growth=0,
            category="essential",
        )
    ]
    result = run(Scenario.model_validate(data), generate(market), binding)
    rows = result["details"][0]["rows"]
    assert sum(r["workplace_contributions"] for r in rows) == 0
    assert rows[-1]["account_balances"]["work_pretax"] > 100000
    assert result["outcomes"][0]["funding_shortfall"] == 12000
    assert not result["outcomes"][0]["funded"]
