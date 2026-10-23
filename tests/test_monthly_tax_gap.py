"""Repeated monthly tax-payment gaps flag funding failure without duplicating liabilities."""

from decimal import Decimal as D

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.annual import Payments
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_example import template


@pytest.mark.parametrize(
    "start,end,timing,unfunded",
    [
        ("2026-09-01", "2026-11-01", "monthly_accrued", D(0)),
        ("2026-12-01", "2027-01-01", "monthly_accrued", D("35468.10")),
        ("2026-12-01", "2027-01-01", "year_end", D("35468.10")),
    ],
)
def test_unpaid_settlement_flags_miss_without_duplicating_liability(
    payload, start, end, timing, unfunded
):
    payload.update(start=start, end=end, incomes=[], expenses=[])
    payload["accounts"][0]["balance"] = "0"
    scenario = Scenario.model_validate(payload)
    plan = template(scenario)
    opening = plan.cases[0].model_copy(
        update=dict(
            federal_income=FederalIncome(wages_primary=D(200000)),
            nj_income=NJIncome(wages=D(200000)),
            payments=Payments(employee_payroll_withheld=D("13818.20")),
        )
    )
    plan = plan.model_copy(update=dict(cases=[opening], settlement_timing=timing))
    rows = project(scenario.model_copy(update={"tax_plan": plan}))
    for row in rows:
        assert row["tax_settlement_payment_gap"] == D("35468.10")
        assert row["funding_failure"]
        assert row["tax_unfunded"] == unfunded
        assert row["net_wealth"] == D("64531.90")
