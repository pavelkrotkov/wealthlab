"""Gross earned wages remain work-test wages despite actual pretax employee deferrals."""

from social_work_household_cases import case, completed

from wealthlab.household.projection import project
from wealthlab.household.records import Account
from wealthlab.retirement.workplace_example import template
from wealthlab.retirement.workplace_inputs import WorkplacePlan


def test_actual_pretax_payroll_reduces_income_tax_wages_without_reducing_work_test_wages():
    scenario = case()
    raw = template(scenario)
    raw.update(
        products={"plan": "pretax_401k"},
        complete_single_employer_elections_confirmed=True,
        gross_wages_before_deferrals_confirmed=True,
        orders=[
            dict(
                id="deferral",
                provenance="illustration",
                date="2026-01-01",
                owner="worker",
                destination="plan",
                kind="pretax_401k",
                amount=1000,
            )
        ],
    )
    raw["years"][0]["contributors"][0].update(workplace_eligible=True, workplace_compensation=30242)
    plan = WorkplacePlan.model_validate(raw)
    account = Account(
        id="plan",
        provenance="illustration",
        owner="worker",
        wrapper="traditional",
        currency="USD",
        balance=0,
        monthly_fee=0,
    )
    scenario = scenario.model_copy(
        update=dict(workplace_plan=plan, accounts=[*scenario.accounts, account])
    )
    rows = project(scenario)
    assert rows[0]["account_balances"]["plan"] == 1000
    assert rows[11]["social_security_government_receivable"] == 491
    assert rows[16]["social_security_refund_cash"] == 491
    assert completed(rows, 2026)["federal"]["agi"] == 30647
