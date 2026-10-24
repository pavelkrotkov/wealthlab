"""The lot book persists through annual eligibility resets and actual cash deposits."""

from copy import deepcopy
from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_example import context
from wealthlab.retirement.hsa_invested_example import synthetic


def test_next_year_cash_deposit_settles_existing_fee_without_reopening_stock_positions():
    scenario = synthetic()
    data = scenario.model_dump(mode="json")
    data["end"] = "2028-01-01"
    next_tax = deepcopy(data["tax_plan"]["cases"][0])
    next_tax["policy"]["year"] = 2027
    data["tax_plan"]["cases"].append(next_tax)
    plan = data["hsa_plan"]
    plan["years"].append(context(scenario, 2027))
    plan["investments"]["case"]["end"] = "2027-12-31"
    plan["investments"]["marks"].append(dict(date="2026-12-31", prices=dict(fund=110)))
    plan["contributions"] = [
        dict(
            id="next_deposit",
            provenance="illustration",
            date="2027-01-01",
            destination="hsa",
            source="direct_employer",
            amount=500,
        )
    ]
    rows = project(Scenario.model_validate(data))
    assert rows[12]["hsa_investment_fees_owed"] == 0
    audit = rows[-1]["hsa_audit"]["investments"]
    assert audit["cash_by_account"]["hsa"] == 450
    assert audit["lots"][0]["quantity"] == "59.983333"
    assert rows[-1]["net_wealth"] == Decimal("7048.17")
    assert audit["nj_income_by_year"][2027] == dict(interest=0, dividends=0, dispositions=0)
