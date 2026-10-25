"""Qualified cash is excluded but still consumes contract cost proportionally."""

from decimal import Decimal

from workplace_roth_cases import aged_data

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_qualified_payments_still_consume_proportional_contract_cost():
    data = aged_data("1960-07-01")
    data["accounts"][1]["balance"] = 23000
    plan = data["workplace_plan"]["roth_cash_withdrawals"]
    plan["contracts"]["ordinary"].update(federal_basis=21850, nj_basis=21000)
    plan["orders"][0]["amount"] = 12000
    row = project(Scenario.model_validate(data))[-1]["workplace_roth_audit"][0]
    assert row["federal_qualified"]
    assert row["federal_basis_recovered"] == 11400
    assert row["federal_basis_remaining"] == 10450
    assert row["nj_basis_remaining"] == Decimal("10043.48")
    assert row["federal_taxable"] == row["nj_taxable"] == 0
    assert row["net_cash"] == 12000
