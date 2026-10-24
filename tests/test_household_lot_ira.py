"""Actual linked-lot gains participate in completed IRA eligibility, not a forecast.

The two cases have the same shares, price and liquidity. Only contribution
basis differs. Zero basis causes funding gains that invalidate the actual
funded Roth deposit; full basis preserves the supported eligibility boundary.
"""

import pytest

from tests.test_household_ira_deposit_sale import funded_by_taxable_sales
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import lot, plan


def actual_lot_case(basis):
    data = funded_by_taxable_sales(basis).model_dump(mode="json")
    linked = plan(Scenario.model_validate(data))
    linked["case"]["accounts"][0]["id"] = "sale_funding"
    holding = lot("funding_holding", "2000", str(basis), str(basis))
    holding["account_id"] = "sale_funding"
    linked["case"]["lots"] = [holding]
    linked["case"]["closing_prices"] = dict(stock="100")
    linked["funding_sources"][0].update(account_id="sale_funding", commission="0")
    data["tax_plan"]["funding_sources"] = []
    data["lot_plan"] = linked
    return Scenario.model_validate(data)


def test_full_basis_actual_shares_preserve_the_funded_roth_eligibility():
    rows = project(actual_lot_case(200000))
    assert rows[-1]["ira_contribution_eligibility"]["roth_ira_magi"] == 236000
    assert sum(r["lot_funding_proceeds"] for r in rows) > 0


def test_actual_share_gains_that_remove_roth_eligibility_block_the_projection():
    with pytest.raises(ValueError, match="Funded Roth IRA contributions exceed"):
        project(actual_lot_case(0))
