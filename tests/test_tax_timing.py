"""Opening YTD is tax context, not new cash; recognized allocations need not distribute cash."""

from datetime import date
from decimal import Decimal as D

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.annual import Payments
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_example import template
from wealthlab.tax.projection_inputs import TaxEvent


def test_partial_first_year_uses_opening_typed_facts_once(payload):
    """Six new wage months plus six opening months produce one annual return.

    Cash starts after opening income and withholding; neither can be reapplied.
    """
    payload.update(start="2026-07-01", end="2027-01-01")
    scenario = Scenario.model_validate(payload)
    plan = template(scenario)
    opening = plan.cases[0].model_copy(
        update={
            "federal_income": FederalIncome(wages_primary=D(60000)),
            "nj_income": NJIncome(wages=D(60000)),
            "payments": Payments(
                federal_income_withheld=D(12000),
                employee_payroll_withheld=D(4590),
                nj_withheld=D(3600),
            ),
        }
    )
    plan = plan.model_copy(update={"cases": [opening]})
    rows = project(scenario.model_copy(update={"tax_plan": plan}))
    assert sum(row["income"] for row in rows) == 60000
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 120000
    assert rows[-1]["closing_cash"] == 115810
    assert rows[-1]["tax_refund_receivable"] == D("17312.50")


def test_tax_allocation_without_distribution_does_not_deposit_cash(payload):
    payload["end"] = "2027-01-01"
    scenario = Scenario.model_validate(payload)
    plan = template(scenario)
    baseline = project(scenario.model_copy(update={"tax_plan": plan}))[-1]
    event = TaxEvent(
        date=date(2026, 1, 10),
        description="Synthetic undistributed interest",
        cash_received=D(0),
        federal=FederalIncome(interest=D(1000)),
        new_jersey=NJIncome(interest=D(1000)),
    )
    plan = plan.model_copy(update={"events": [event]})
    rows = project(scenario.model_copy(update={"tax_plan": plan}))
    assert sum(row["tax_event_cash"] for row in rows) == 0
    assert rows[-1]["closing_cash"] == baseline["closing_cash"]
    assert baseline["net_wealth"] - rows[-1]["net_wealth"] == D("175.25")
