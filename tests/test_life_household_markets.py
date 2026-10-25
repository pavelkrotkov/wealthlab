"""A supplied policy path stays conditional while the actual funding portfolio varies.

The policy is deliberately not treated as market-priced equity. On the same
realized batch, repeated household runs must use the same cash, trades and taxes;
the unmodeled-return confirmation remains necessary for the supplied policy marks.
"""

import pytest

from tests.test_life_household_funding import funded_data
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_example import synthetic
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


def realized(mode, household):
    _, market, binding = synthetic(mode)
    data = market.model_dump(mode="json")
    data["end"] = str(household.end)
    if data["historical"] is not None:
        data["historical"]["months"] = data["historical"]["months"][:3]
    data["shocks"] = [s for s in data["shocks"] if s["month"] < 3]
    return generate(MarketCase.model_validate(data)), binding


@pytest.mark.parametrize("mode", ["deterministic", "historical", "monte_carlo", "stress"])
def test_actual_policy_funding_replays_on_the_same_realized_batch(mode):
    household = Scenario.model_validate(funded_data())
    batch, binding = realized(mode, household)
    left = run(household, batch, binding, indices=[0])
    right = run(household, batch, binding, indices=[0])
    assert paired(left, right)[0]["real_wealth_change"] == 0
    rows = left["details"][0]["rows"]
    assert sum(r["life_payments_paid"] for r in rows) == 2000
    assert rows[-1]["account_balances"]["life_policy"] == 11500
    assert rows[-1]["life_policy_values"][0]["loan"] == 500
    assert "life_policy_audit" in rows[-1]
