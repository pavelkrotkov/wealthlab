"""Synthetic two-year wages, IRA deposits, withdrawals and a later regular-Roth draw."""

from decimal import Decimal

from wealthlab.household.example import synthetic as working_household
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.ira_household_example import synthetic as withdrawals
from wealthlab.retirement.ira_household_inputs import IRAPlan
from wealthlab.tax.projection_example import template as tax_template


def synthetic():
    data = withdrawals().model_dump(mode="json")
    data.update(name="Synthetic IRA contribution household", inflation=0)
    for p in data["members"]:
        p["retirement_date"] = "2030-01-01"
    data["accounts"][0]["balance"] = "10000"
    salary = working_household().incomes[0].model_dump(mode="json")
    salary.update(monthly_amount="5000", end="2028-01-01")
    data["incomes"] = [salary]
    data["expenses"][0]["monthly_amount"] = "2000"
    data["ira_plan"]["orders"].append(
        dict(
            id="roth_regular_draw",
            provenance="illustration",
            date="2027-10-01",
            source="roth",
            destination=None,
            kind="withdrawal",
            amount="5000",
            early_penalty_exception=False,
        )
    )
    case = Scenario.model_validate(data)
    deposits = template(case)
    ira = IRAPlan.model_validate(dict(data["ira_plan"], contributions=deposits))
    taxes = tax_template(case).model_copy(
        update=dict(federal_wage_withholding=Decimal(0), nj_wage_withholding=Decimal(0))
    )
    return case.model_copy(update=dict(ira_plan=ira, tax_plan=taxes))


def template(scenario):
    return dict(
        years=[context(scenario, year) for year in range(scenario.start.year, scenario.end.year)],
        orders=[
            dict(
                id=f"deposit_{year}_{kind}",
                provenance="illustration",
                date=f"{year}-{month}-15",
                owner=scenario.members[0].id,
                destination=destination,
                kind=kind,
                amount="3000",
            )
            for year in range(scenario.start.year, scenario.end.year)
            for kind, month, destination in (
                ("traditional_ira", "01", "retirement"),
                ("roth_ira", "07", "roth"),
            )
        ],
        complete_annual_elections_and_context_confirmed=True,
        timing="month_end_after_receipts_before_current_tax_and_spending",
    )


def context(scenario, year):
    return dict(
        year=year,
        rule_mode="freeze_2026_assumption",
        filing="joint",
        lived_with_spouse=True,
        spouse_covered_by_workplace_plan=False,
        contributors=[
            dict(
                id=p.id,
                provenance="illustration",
                birth_date=p.birth_date.isoformat(),
                eligible_ira_compensation="60000" if i == 0 else "0",
                ira_compensation_budget="60000" if i == 0 else "0",
                workplace_compensation="0",
                traditional_ira_magi="70000",
                roth_ira_magi="70000",
                covered_by_workplace_plan=False,
                prior_employer_wages="0",
                workplace_eligible=False,
                catchup_permitted=False,
            )
            for i, p in enumerate(scenario.members)
        ],
    )
