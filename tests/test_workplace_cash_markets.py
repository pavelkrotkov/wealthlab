"""All four path methods retain actual gross debits and source-withheld liquidity.

Plan returns stay inside the plan. With the example's zero final liability,
ending wealth must equal opening $100,000 plus actual investment change;
$8,000 deposited into an HSA and $2,000 source tax are internal movements.
"""

import pytest

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.markets.workplace_example import synthetic as market_example
from wealthlab.retirement.workplace_withdrawal_example import synthetic


@pytest.mark.parametrize("mode", ["deterministic", "historical", "monte_carlo", "stress"])
def test_actual_withdrawals_and_source_credits_survive_realized_market_execution(mode):
    _, market, binding = market_example(mode)
    data = synthetic().model_dump(mode="json")
    data["end"] = "2027-01-01"
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    data["workplace_plan"]["years"] = data["workplace_plan"]["years"][:1]
    data["hsa_plan"]["years"] = data["hsa_plan"]["years"][:1]
    household = Scenario.model_validate(data)
    binding = binding.model_copy(update=dict(wrappers=binding.wrappers[:1]))
    batch = generate(market)
    result = run(household, batch, binding, [0])
    rows = result["details"][0]["rows"]
    assert rows[1]["workplace_withdrawal_gross"] == 10000
    assert rows[1]["hsa_personal_contributions"] == 8000
    assert sum(r["tax_source_withholding"] for r in rows) == 2000
    assert rows[-1]["net_wealth"] == 100000 + sum(r["workplace_market_change"] for r in rows)
    assert result["outcomes"][0]["gross_cash_taxes_paid"] == 2000
