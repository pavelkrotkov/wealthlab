"""Representable Roth, RMD and cash-only profiles share real household funding.

Annual spending deliberately leaves a remainder after twelve cent-rounded
monthly payments. December receives that remainder exactly once. RMDs use
actual prior-year balances; the reference is not allowed to hide a shortfall.
"""

from decimal import Decimal as D

import pytest

from wealthlab.retirement.owl_household_inputs import OwlHouseholdCase, synthetic
from wealthlab.retirement.owl_household_reference import run


@pytest.fixture(scope="module")
def roth_rmd():
    data = synthetic().model_dump()
    data.update(
        age=75,
        years=2,
        cash=50000,
        traditional_ira=50000,
        nj_ira_basis=50000,
        roth_ira=30000,
        roth_first_year=2010,
        annual_spending="30000.01",
    )
    result = run(OwlHouseholdCase.model_validate(data))
    return result


def test_qualified_roth_and_cent_spending(roth_rmd):
    result = roth_rmd
    assert not result["funding_failure"]
    assert result["unfilled_ira_requests"] == 0
    assert result["max_absolute_wealth_residual"] <= D(".02")
    assert [r["native_spending_paid"] for r in result["rows"]] == [D("30000.01")] * 2


def test_cash_only_case_does_not_require_taxable_ira_income():
    data = synthetic().model_dump()
    data.update(years=2, cash=100000, traditional_ira=0, nj_ira_basis=0)
    result = run(OwlHouseholdCase.model_validate(data))
    assert result["rows"][0]["native_marked_wealth"] == 70000
    assert result["rows"][0]["native_federal_tax"] == 0
    assert result["reference"]["estate_proxy"] == pytest.approx(40000)


def test_actual_rmd_targets_remain_visible(roth_rmd):
    result = roth_rmd
    rmd = result["household_months"][11]["ira_annual_reconciliation"]["rmd"]["person_a"]
    assert rmd["required"] == D("2032.53")
    assert rmd["withdrawn"] >= rmd["required"]
    assert all(r["native_rmd_shortfall"] == 0 for r in result["rows"])
