"""Actual tax-funding gains must not preserve stale Roth eligibility."""

import pytest

from tests.ira_deposit_household_cases import one_year
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def funded_by_taxable_sales(basis):
    data = one_year().model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["accounts"].append(
        dict(
            id="sale_funding",
            provenance="illustration",
            owner="person_a",
            currency="USD",
            wrapper="taxable",
            balance="200000",
            monthly_fee="0",
        )
    )
    data["tax_plan"]["funding_sources"] = [
        dict(
            account_id="sale_funding",
            federal_basis=str(basis),
            nj_basis=str(basis),
            federal_character="long_term",
            loss_treatment="allowed",
            liquid_after="2025-12-31",
        )
    ]
    data["incomes"][0]["monthly_amount"] = "18000"
    data["expenses"][0]["monthly_amount"] = "18500"
    return Scenario.model_validate(data)


def test_equal_liquidity_with_no_gain_supports_the_funded_roth_deposit():
    rows = project(funded_by_taxable_sales(200000))
    assert rows[-1]["ira_contribution_eligibility"]["roth_ira_magi"] == 236000
    assert sum(r["funding_sale_proceeds"] for r in rows) > 0


def test_tax_funding_gain_that_removes_roth_eligibility_blocks_the_result():
    with pytest.raises(ValueError, match="Funded Roth IRA contributions exceed"):
        project(funded_by_taxable_sales(0))
