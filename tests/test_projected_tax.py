"""End-to-end cash conservation, refund timing and annual recognized income."""

from decimal import Decimal as D

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.projection_example import template


def taxed(payload):
    scenario = Scenario.model_validate(payload)
    return scenario.model_copy(update={"tax_plan": template(scenario)})


def test_tax_and_delayed_refunds_reconcile_to_household_wealth(payload):
    rows = project(taxed(payload))
    december, march, april, last = rows[11], rows[14], rows[15], rows[-1]
    # 120k wages: 10143 federal income + 9180 payroll + 3744.50 NJ.
    assert december["annual_tax"]["total_liability"] == D("23067.50")
    assert december["tax_refund_receivable"] == D("17312.50")
    assert (march["tax_refund_received"], april["tax_refund_received"]) == (0, D("17312.50"))
    assert last["closing_cash"] == D("100932.50")
    assert last["net_wealth"] == D("200932.50")
    assert sum(row["funding_shortfall"] for row in rows) == 0
    assert sum(row["income"] for row in rows) == 120000


def test_unfunded_taxes_remain_a_liability(payload):
    payload["end"] = "2027-01-01"
    payload["accounts"][0]["balance"] = "0"
    payload["expenses"][0]["monthly_amount"] = "10000"
    scenario = taxed(payload)
    plan = scenario.tax_plan.model_copy(
        update={"federal_wage_withholding": D(0), "nj_wage_withholding": D(0)}
    )
    rows = project(scenario.model_copy(update={"tax_plan": plan}))
    last = rows[-1]
    assert last["closing_cash"] == 0
    assert last["tax_owed"] > 0
    assert last["net_wealth"] == D(100000) - last["tax_owed"]
    assert last["tax_unfunded"] == last["tax_owed"]
    assert last["annual_tax"]["federal"]["agi"] == 120000
