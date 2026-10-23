"""Explicit liquid-account sales fund their own tax while preserving jurisdiction basis."""

from datetime import date
from decimal import Decimal as D

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.annual import Payments
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.liquidation import FundingSource
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_example import template


def scenario(payload, nj_basis="0", liquid_after=date(2026, 1, 1)):
    payload.update(start="2026-12-01", end="2027-01-01", incomes=[])
    payload["expenses"][0]["monthly_amount"] = "10000"
    payload["accounts"][0]["balance"] = "0"
    payload["accounts"][1].update(wrapper="taxable", id="brokerage", balance="100000")
    household = Scenario.model_validate(payload)
    plan = template(household)
    case = plan.cases[0].model_copy(
        update={
            "federal_income": FederalIncome(wages_primary=D(200000)),
            "nj_income": NJIncome(wages=D(200000)),
            "payments": Payments(
                federal_income_withheld=D(26898),
                employee_payroll_withheld=D("13818.20"),
                nj_withheld=D("8570.10"),
            ),
        }
    )
    source = FundingSource(
        account_id="brokerage",
        federal_basis=D(0),
        nj_basis=D(nj_basis),
        federal_character="long_term",
        loss_treatment="allowed",
        liquid_after=liquid_after,
    )
    return household.model_copy(
        update={"tax_plan": plan.model_copy(update={"cases": [case], "funding_sources": [source]})}
    )


@pytest.mark.parametrize(("nj_basis", "expected_sale"), [("0", "12717.79"), ("100000", "11764.70")])
def test_sale_funds_spending_and_its_own_tax(payload, nj_basis, expected_sale):
    """At $200k opening wages, extra LT gains face 15% federal plus 6.37% NJ.

    The second case has full NJ basis, so only the 15% federal rate applies.
    No NIIT arises because the resulting income remains below $250k.
    """
    row = project(scenario(payload, nj_basis))[-1]
    assert row["funding_sale_proceeds"] == D(expected_sale)
    assert row["funding_shortfall"] == 0
    assert row["tax_owed"] == 0
    assert row["closing_cash"] == 0
    assert row["net_wealth"] == 100000 - D(expected_sale)


def test_locked_account_cannot_fund_spending(payload):
    row = project(scenario(payload, liquid_after=date(2027, 1, 1)))[-1]
    assert row["funding_sale_proceeds"] == 0
    assert row["funding_shortfall"] == 10000
    assert row["account_balances"]["brokerage"] == 100000
