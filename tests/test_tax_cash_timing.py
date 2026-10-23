"""Estimated payments and jurisdiction refunds affect cash without changing tax character."""

from datetime import date
from decimal import Decimal as D

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.annual import Payments
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_example import template
from wealthlab.tax.projection_inputs import EstimatedPayment


def test_estimated_payment_is_cash_now_and_refund_later(payload):
    scenario = Scenario.model_validate(payload)
    plan = template(scenario)
    baseline = project(scenario.model_copy(update={"tax_plan": plan}))
    extra = EstimatedPayment(date=date(2026, 1, 15), federal=D(1000), new_jersey=D(500))
    rows = project(
        scenario.model_copy(
            update={"tax_plan": plan.model_copy(update={"estimated_payments": [extra]})}
        )
    )
    assert rows[0]["tax_estimates_paid"] == 1500
    assert baseline[0]["closing_cash"] - rows[0]["closing_cash"] == 1500
    assert rows[15]["tax_refund_received"] - baseline[15]["tax_refund_received"] == 1500
    assert rows[-1]["net_wealth"] == baseline[-1]["net_wealth"]


def test_nj_refund_cannot_fund_current_federal_bill(payload):
    """NJ overpayment is an asset, but cannot settle the unpaid federal bill.

    Netting the jurisdictions would understate the immediate funding shortfall.
    """
    payload.update(start="2026-12-01", end="2027-01-01", incomes=[])
    payload["accounts"][0]["balance"] = "0"
    scenario = Scenario.model_validate(payload)
    plan = template(scenario)
    opening = plan.cases[0].model_copy(
        update={
            "federal_income": FederalIncome(wages_primary=D(200000)),
            "nj_income": NJIncome(wages=D(200000)),
            "payments": Payments(employee_payroll_withheld=D("13818.20"), nj_withheld=D(30000)),
        }
    )
    row = project(
        scenario.model_copy(update={"tax_plan": plan.model_copy(update={"cases": [opening]})})
    )[-1]
    assert row["tax_owed"] == 26898
    assert row["tax_refund_receivable"] == D("21429.90")
    assert row["tax_unfunded"] == 26898
    assert row["closing_cash"] == 0


def test_missed_estimate_is_a_timing_failure_without_invented_debt(payload):
    payload.update(incomes=[], expenses=[])
    payload["accounts"][0]["balance"] = "0"
    scenario = Scenario.model_validate(payload)
    plan = template(scenario).model_copy(
        update={
            "estimated_payments": [
                EstimatedPayment(date=date(2026, 1, 15), federal=D(1000), new_jersey=D(0))
            ]
        }
    )
    row = project(scenario.model_copy(update={"tax_plan": plan}))[0]
    assert row["tax_payment_gap"] == 1000
    assert row["funding_failure"]
    assert row["tax_owed"] == 0
    assert row["net_wealth"] == 100000
