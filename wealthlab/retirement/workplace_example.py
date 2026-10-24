"""Independent synthetic household with shared pretax/Roth employee elections."""

from datetime import date
from decimal import Decimal

from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_inputs import WorkplacePlan
from wealthlab.tax.projection_example import template as tax_template


def template(scenario):
    return dict(
        years=[
            dict(
                year=year,
                rule_mode="freeze_2026_assumption" if year >= 2026 else "published",
                contributors=[
                    dict(
                        id=p.id,
                        provenance="assumption",
                        birth_date=p.birth_date.isoformat(),
                        workplace_compensation=0,
                        prior_employer_wages=0,
                        workplace_eligible=False,
                        catchup_permitted=False,
                    )
                    for p in scenario.members
                ],
            )
            for year in range(scenario.start.year, scenario.end.year)
        ],
        products={},
        orders=[],
        complete_single_employer_elections_confirmed=False,
        gross_wages_before_deferrals_confirmed=False,
        timing="monthly_payroll_before_tax_and_spending",
    )


def synthetic():
    data = household().model_dump(mode="json")
    data.update(
        name="Synthetic employee 401(k) household",
        start="2026-01-01",
        end="2027-01-01",
        inflation=0,
        contributions=[],
        debts=[],
    )
    for member in data["members"]:
        member["retirement_date"] = "2030-01-01"
    data["accounts"] = [
        dict(
            id="cash",
            owner="person_a",
            wrapper="cash",
            balance="100000",
            currency="USD",
            monthly_fee="0",
            provenance="illustration",
        )
    ]
    for aid, wrapper in (("work_pretax", "traditional"), ("work_roth", "roth")):
        data["accounts"].append(
            dict(
                id=aid,
                owner="person_a",
                wrapper=wrapper,
                balance="0",
                currency="USD",
                monthly_fee="0",
                provenance="illustration",
            )
        )
    data["incomes"][0].update(end="2027-01-01", monthly_amount="10000", annual_growth=0)
    data["expenses"] = []
    case = Scenario.model_validate(data)
    plan = template(case)
    plan.update(
        products={"work_pretax": "pretax_401k", "work_roth": "roth_401k"},
        complete_single_employer_elections_confirmed=True,
        gross_wages_before_deferrals_confirmed=True,
    )
    primary = plan["years"][0]["contributors"][0]
    primary.update(workplace_compensation="120000", workplace_eligible=True)
    plan["orders"] = elections()
    taxes = tax_template(case).model_copy(
        update=dict(federal_wage_withholding=Decimal(0), nj_wage_withholding=Decimal(0))
    )
    return case.model_copy(
        update=dict(workplace_plan=WorkplacePlan.model_validate(plan), tax_plan=taxes)
    )


def elections():
    orders = [
        dict(
            id=f"pretax_{month}",
            provenance="illustration",
            date=date(2026, month, 1).isoformat(),
            owner="person_a",
            destination="work_pretax",
            kind="pretax_401k",
            amount="2000",
        )
        for month in range(1, 13)
    ]
    orders.append(
        dict(
            id="roth_dec",
            provenance="illustration",
            date="2026-12-15",
            owner="person_a",
            destination="work_roth",
            kind="roth_401k",
            amount="2000",
        )
    )
    return orders
