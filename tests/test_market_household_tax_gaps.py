"""An unpaid December balance is a tax schedule miss even when every payroll was paid.

Wages cover each month's employee payroll, but zero income-tax withholding
leaves a December bill larger than that month's remaining cash. Locked stock
cannot fill the gap. The actual failure, tax UI and outcome counter must agree.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_example import synthetic
from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.tax.payments import missed_schedule


def test_only_settlement_underfunding_is_still_a_missed_tax_schedule_month():
    household, market, binding = synthetic()
    data = household.model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["incomes"][0]["monthly_amount"] = "10000"
    data["expenses"][0]["monthly_amount"] = "9200"
    paths = market.model_dump(mode="json")
    paths.update(
        mode="stress",
        shocks=[dict(name="unavailable taxable stock", month=0, lock_months=dict(equities=24))],
    )
    result = run(Scenario.model_validate(data), generate(MarketCase.model_validate(paths)), binding)
    rows = result["details"][0]["rows"]
    assert all(r["tax_payment_gap"] == 0 for r in rows)
    assert rows[11]["tax_settlement_payment_gap"] > 0
    assert result["outcomes"][0]["first_failure"] == "2026-12-01"
    assert sum(missed_schedule(r) for r in rows) == 1
    assert result["outcomes"][0]["missed_tax_schedule_months"] == 1
