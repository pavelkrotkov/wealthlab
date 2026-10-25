"""Plan age55 access changes the additional tax, while Roth owner-lifetime RMDs stay absent."""

from workplace_roth_cases import aged_data

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_roth_example import synthetic


def test_age55_separation_exempts_earnings_penalty_without_qualifying_the_payment():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["roth_cash_withdrawals"]["contracts"]["ordinary"]["separation_date"] = (
        "2026-01-01"
    )
    row = project(Scenario.model_validate(data))[-1]["workplace_roth_audit"][0]
    assert row["separation_age55_exception"]
    assert not row["federal_qualified"]
    assert row["federal_taxable"] == 300
    assert row["additional_tax"] == 0


def test_ordinary_owner_lifetime_roth_plan_needs_no_rmd_cash_or_age1959_choice():
    data = aged_data("1951-07-01")
    data["workplace_plan"]["roth_cash_withdrawals"]["orders"] = []
    rows = project(Scenario.model_validate(data))
    assert rows[-1]["account_balances"]["work_roth"] == 10000
    assert rows[-1]["workplace_roth_audit"] == []
    assert rows[-1]["workplace_rmd_audit"] == []
    assert rows[-1]["net_wealth"] == 10000
