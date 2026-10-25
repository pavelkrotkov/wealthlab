"""Synthetic age-55 separation retains plan access and funds only net HSA cash.

The participant turns 55 in July but separates in January of that calendar
year. A February $10,000 plan distribution therefore has no age-based 10%
additional tax in this ordinary profile. $2,000 withholding remains unavailable
for the requested $8,500 HSA deposit; only $8,000 reaches that account.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_example import context
from wealthlab.retirement.workplace_example import template
from wealthlab.tax.source_example import synthetic as source_household


def synthetic():
    data = source_household().model_dump(mode="json")
    data["name"] = "Synthetic 401(k) separation access and source withholding"
    data["members"][0]["birth_date"] = "1971-07-01"
    data["accounts"].append(
        dict(
            id="work_pretax",
            owner="person_a",
            wrapper="traditional",
            balance=100000,
            currency="USD",
            monthly_fee=0,
            provenance="illustration",
        )
    )
    data["tax_plan"]["events"] = []
    scenario = Scenario.model_validate(data)
    data["hsa_plan"]["years"] = [context(scenario, year) for year in (2026, 2027)]
    plan = template(scenario)
    plan.update(
        products=dict(work_pretax="pretax_401k"),
        complete_single_employer_elections_confirmed=True,
        gross_wages_before_deferrals_confirmed=True,
        cash_withdrawals=dict(
            profiles=dict(work_pretax=profile()),
            orders=[
                dict(
                    id="separated_cash",
                    provenance="illustration",
                    date="2026-02-01",
                    source="work_pretax",
                    amount=10000,
                    federal_withholding_rate=".20",
                    nj_withholding_rate=0,
                )
            ],
            timing="first_day_before_employee_deferrals_and_month_end_returns",
        ),
    )
    data["workplace_plan"] = plan
    return Scenario.model_validate(data)


def profile():
    return dict(
        separation_date="2026-01-01",
        eligible_nonperiodic_cash_distributions_confirmed=True,
        fully_vested_zero_federal_and_nj_basis_confirmed=True,
        no_inherited_loans_nua_hardship_or_other_special_features_confirmed=True,
        complete_distributions_excluded_from_other_inputs_confirmed=True,
    )
