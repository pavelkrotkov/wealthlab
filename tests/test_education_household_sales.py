"""Funding sales quote tuition after wrapper payments instead of selling twice."""

from tests.test_education_household_cash import cash_only_data
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def funded_data():
    data = cash_only_data()
    data["accounts"].append(
        dict(
            id="brokerage",
            provenance="illustration",
            owner="person_a",
            wrapper="taxable",
            currency="USD",
            balance="100000",
            monthly_fee="0",
        )
    )
    data["tax_plan"]["funding_sources"] = [
        dict(
            account_id="brokerage",
            federal_basis="100000",
            nj_basis="100000",
            federal_character="long_term",
            loss_treatment="allowed",
            liquid_after="2025-01-01",
        )
    ]
    data["education_plan"]["tuition"] = [
        dict(
            id="bill", provenance="illustration", source="college", date="2026-09-01", amount="1000"
        )
    ]
    return data


def test_fully_wrapper_paid_tuition_needs_no_extra_taxable_sale():
    data = funded_data()
    paid = project(Scenario.model_validate(data))
    data["education_plan"]["tuition"] = []
    baseline = project(Scenario.model_validate(data))
    assert sum(r["funding_sale_proceeds"] for r in paid) == sum(
        r["funding_sale_proceeds"] for r in baseline
    )
    assert baseline[-1]["net_wealth"] - paid[-1]["net_wealth"] == 1000


def test_cash_fallback_can_use_explicit_permitted_sales():
    data = funded_data()
    data["accounts"][0]["balance"] = "0"
    data["education_plan"]["tuition"][0]["amount"] = "20000"
    rows = project(Scenario.model_validate(data))
    assert sum(r["education_wrapper_paid"] for r in rows) == 1000
    assert sum(r["education_cash_fallback"] for r in rows) == 19000
    assert sum(r["education_unfunded"] for r in rows) == 0
