"""Scheduled other income supplies actual cash once without wage payroll/withholding."""

from wealthlab.household.example import synthetic
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.projection_example import template
from wealthlab.tax.projection_inputs import IncomeRule


def test_other_income_schedule_flows_to_actual_cash_and_one_annual_return():
    data = synthetic().model_dump(mode="json")
    cash = next(a for a in data["accounts"] if a["wrapper"] == "cash")
    cash.update(balance="100000", monthly_fee="0")
    data.update(
        end="2027-01-01",
        accounts=[cash],
        expenses=[],
        debts=[],
        contributions=[],
        incomes=[
            dict(
                id="other_cash",
                provenance="assumption",
                owner="person_a",
                currency="USD",
                start="2026-01-01",
                end="2027-01-01",
                monthly_amount="5000",
                annual_growth=0,
                stop_at_retirement=False,
            )
        ],
    )
    case = Scenario.model_validate(data)
    plan = template(case).model_copy(
        update=dict(
            income_rules=[
                IncomeRule(
                    income_id="other_cash",
                    federal="ordinary_noninvestment_income",
                    new_jersey="other",
                )
            ]
        )
    )
    rows = project(case.model_copy(update=dict(tax_plan=plan)))
    final = rows[-1]
    assert sum(r["income"] for r in rows) == final["annual_tax"]["federal"]["agi"] == 60000
    assert final["annual_tax"]["federal"]["employee_payroll"] == 0
    assert sum(r["tax_withheld"] for r in rows) == 0
    assert (
        final["closing_cash"]
        == final["net_wealth"]
        == 160000 - final["annual_tax"]["total_liability"]
    )
