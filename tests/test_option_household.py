"""Actual option assignment funds household spending and recognizes separate jurisdiction gains."""

from wealthlab.household.projection import project
from wealthlab.products.option_household_example import synthetic


def test_assignment_enters_shared_cash_actual_shares_basis_and_annual_income_once():
    rows = project(synthetic())
    assert rows[0]["closing_cash"] == 1000
    assert rows[1]["closing_cash"] == 11500
    assert rows[1]["option_shares"] == 0
    assert rows[-1]["closing_cash"] == rows[-1]["net_wealth"] == 6500
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 6500
    assert rows[-1]["annual_tax"]["new_jersey"]["gross_income"] == 5500
    assert rows[-1]["option_lots"] == []


def test_actual_option_income_changes_year_end_tax_cash_using_existing_annual_engine():
    from wealthlab.household.scenario import Scenario

    data = synthetic().model_dump(mode="json")
    annual = data["tax_plan"]["cases"][0]
    annual["federal_income"]["interest"] = "100000"
    annual["nj_income"]["interest"] = "100000"
    data["accounts"][0]["balance"] = "100000"
    rows = project(Scenario.model_validate(data))
    tax = rows[-1]["annual_tax"]
    assert tax["federal"]["agi"] == 106500
    assert tax["new_jersey"]["gross_income"] == 105500
    assert rows[-1]["closing_cash"] == 105500 - tax["total_liability"]
