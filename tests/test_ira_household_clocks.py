"""The household adapter retains the existing IRA engine's RMD and Roth clocks."""

from datetime import date
from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.retirement.ira_household_example import synthetic
from wealthlab.tax.projection_example import template as tax_template


def test_conversion_cannot_precede_required_ira_cash_withdrawal():
    c = synthetic()
    birth = date(1951, 6, 15)
    members = [c.members[0].model_copy(update=dict(birth_date=birth)), c.members[1]]
    owners = [c.ira_plan.owners[0].model_copy(update=dict(birth_date=birth)), c.ira_plan.owners[1]]
    orders = [
        c.ira_plan.orders[0].model_copy(update=dict(date=date(2026, 12, 1))),
        *c.ira_plan.orders[1:],
    ]
    plan = c.ira_plan.model_copy(update=dict(owners=owners, orders=orders))
    c = c.model_copy(update=dict(members=members, ira_plan=plan))
    rows = project(c.model_copy(update=dict(tax_plan=tax_template(c))))
    assert rows[6]["ira_conversion_value"] == 0
    assert rows[6]["ira_unfilled_requests"] == 10000
    required = rows[11]["ira_annual_reconciliation"]["rmd"]["person_a"]
    assert required == dict(
        required=Decimal("4065.05"), withdrawn=20000, shortfall=0, divisor=Decimal("24.6")
    )


def test_later_roth_draw_uses_carried_conversion_clock_and_nj_basis():
    c = synthetic()
    order = c.ira_plan.orders[0].model_copy(
        update=dict(id="roth_2027", source="roth", date=date(2027, 6, 1), amount=Decimal(10000))
    )
    plan = c.ira_plan.model_copy(update=dict(orders=[*c.ira_plan.orders, order]))
    rows = project(c.model_copy(update=dict(ira_plan=plan)))
    result = rows[-1]["ira_annual_reconciliation"]
    roth = next(r for r in result["orders"] if r["id"] == "roth_2027")
    assert roth["conversion_recapture"] == 10000
    assert roth["additional_tax"] == 1000
    assert roth["federal_taxable"] == roth["nj_taxable"] == 0
    assert result["owners"][0]["nj_roth_basis"] == 0
    assert rows[-1]["annual_tax"]["total_liability"] == 3000
