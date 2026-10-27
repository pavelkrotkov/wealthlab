"""Synthetic wrapper policies share opening assets, tuition and prior medical receipts.

The short illustration still uses the default age-100 target. Whole-account
proxies do not certify issuer inventories: the default concentration constraint
remains enabled and reports that missing information instead of assuming it.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.retirement.education_household_example import plan as education_plan
from wealthlab.retirement.hsa_household_example import plan as hsa_plan
from wealthlab.retirement.workplace_example import template as workplace_plan
from wealthlab.retirement.workplace_withdrawal_example import profile


def extend(case):
    data = case.model_dump(mode="json")
    household = data["household"]
    common = dict(owner="person_a", provenance="illustration", currency="USD", monthly_fee="0")
    household["accounts"] += [
        dict(common, id="work_pretax", wrapper="traditional", balance="10000"),
        dict(common, id="cash_hsa", wrapper="hsa", balance="10000"),
        dict(common, id="college", wrapper="education", balance="6000"),
    ]
    household["name"] = "Synthetic policy search with actual workplace, HSA and 529 cash"
    scenario = Scenario.model_validate(household)
    household["workplace_plan"] = workplace(scenario)
    household["hsa_plan"] = hsa(scenario)
    household["education_plan"] = education()
    data["dimensions"].append(
        dict(
            id="account_cash_timing",
            choices=[
                dict(
                    id=timing,
                    workplace_cash_orders=[cash_order(year)],
                    hsa_withdrawals=[
                        dict(household["hsa_plan"]["withdrawals"][0], date=f"{year}-01-01")
                    ],
                    hsa_personal_contributions=[],
                    education_contributions=[],
                )
                for timing, year in (("early", 2026), ("later", 2027))
            ],
        )
    )
    return PolicySearch.model_validate(data)


def cash_order(year):
    return dict(
        id="work_cash",
        provenance="illustration",
        date=f"{year}-01-01",
        source="work_pretax",
        amount="10000",
        federal_withholding_rate=".20",
    )


def workplace(scenario):
    plan = workplace_plan(scenario)
    plan.update(
        products=dict(work_pretax="pretax_401k"),
        complete_single_employer_elections_confirmed=True,
        gross_wages_before_deferrals_confirmed=True,
        cash_withdrawals=dict(
            profiles=dict(work_pretax=profile()),
            orders=[cash_order(2026)],
            timing="first_day_before_employee_deferrals_and_month_end_returns",
        ),
    )
    return plan


def hsa(scenario):
    plan = hsa_plan(scenario)
    plan.update(contributions=[], interest=[])
    plan["medical_receipts"][0]["amount"] = "12000"
    plan["withdrawals"] = [dict(plan["withdrawals"][0], amount="10000", date="2026-01-01")]
    return plan


def education():
    plan = education_plan()
    plan.update(contributions=[], returns=[])
    plan["accounts"][0]["contribution_basis"] = "6000"
    for payment in plan["tuition"]:
        payment["amount"] = "3000"
    return plan
