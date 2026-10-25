"""Separate policy and option books preserve their cash and liability accounting.

The covered-call account starts with $10,000 stock and ultimately receives
$11,000 strike delivery plus $500 premium. Its $11,500 after-tax contribution
must add once to the independent policy household's $57,000 ending wealth.
"""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_household_example import synthetic as life
from wealthlab.products.option_household_example import synthetic as options


def combined():
    data = life().model_dump(mode="json")
    option = options().model_dump(mode="json")
    data["accounts"].append(option["accounts"][1])
    plan = option["option_plan"]
    plan["case"]["holdings"]["end"] = "2026-03-31"
    plan["case"]["marks"] = [m for m in plan["case"]["marks"] if m["date"] <= "2026-03-31"]
    data["option_plan"] = plan
    return Scenario.model_validate(data)


def test_options_and_life_share_receipts_and_tax_without_losing_either_ledger():
    row = project(combined())[-1]
    assert row["net_wealth"] == 68500
    assert row["closing_cash"] == 57000
    assert row["account_balances"]["life_policy"] == 11500
    assert row["account_balances"]["options"] == 0
    assert row["life_policy_values"][0]["loan"] == 500
    assert "life_policy_audit" in row
    assert "option_audit" in row
