"""Two distinct synthetic plans require independent withdrawals; subaccounts share a target.

At age75, two $246,000 plans each require $10,000 using divisor24.6.
The alpha plan's $15,000 February withdrawal includes $10,000 RMD and
$5,000 eligible remainder; only beta needs December catch-up. No gains,
spending or final tax liability means all $492,000 opening wealth is conserved.
"""

from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_example import template
from wealthlab.retirement.workplace_withdrawal_example import profile
from wealthlab.tax.projection_example import template as tax_plan


def synthetic():
    data = household().model_dump(mode="json")
    data.update(
        name="Synthetic separate-plan RMDs and source withholding",
        incomes=[],
        expenses=[],
        contributions=[],
        debts=[],
    )
    data["members"][0]["birth_date"] = "1951-07-01"
    data["members"][1]["birth_date"] = "1965-07-01"
    data["accounts"] = [account("cash", "cash", 0)]
    data["accounts"] += [
        account(name, "traditional", value)
        for name, value in (("alpha_one", 123000), ("alpha_two", 123000), ("beta", 246000))
    ]
    scenario = Scenario.model_validate(data)
    plan = template(scenario)
    plan.update(
        products={name: "pretax_401k" for name in ("alpha_one", "alpha_two", "beta")},
        complete_single_employer_elections_confirmed=True,
        gross_wages_before_deferrals_confirmed=True,
        cash_withdrawals=cash_plan(),
    )
    data["workplace_plan"] = plan
    data["tax_plan"] = tax_plan(scenario).model_dump(mode="json")
    return Scenario.model_validate(data)


def account(identity, wrapper, balance):
    return dict(
        id=identity,
        owner="person_a",
        currency="USD",
        wrapper=wrapper,
        balance=balance,
        monthly_fee=0,
        provenance="illustration",
    )


def cash_plan():
    return dict(
        profiles={s: profile() for s in ("alpha_one", "alpha_two", "beta")},
        orders=[
            dict(
                id="alpha_cash",
                provenance="illustration",
                date="2026-02-01",
                source="alpha_one",
                amount=15000,
            )
        ],
        timing="first_day_before_employee_deferrals_and_month_end_returns",
        rmd=dict(
            groups=dict(alpha=group(["alpha_one", "alpha_two"]), beta=group(["beta"])),
            rule_mode="frozen_2026_rmd_rules_assumption",
            deadline="december_target_no_first_year_deferral",
            automatic_december_catchup=True,
            no_unmodeled_opening_shortfalls_confirmed=True,
        ),
    )


def group(sources):
    return dict(
        sources=sources,
        complete_distinct_plan_balances_and_distributions_confirmed=True,
        beneficiary_table_eligibility_confirmed=True,
        rmd_table="uniform",
    )
