"""A one-year direct-bill cash stress with no other spending or tax assumptions."""

from datetime import date
from decimal import Decimal

from wealthlab.retirement.medicare_household_example import synthetic
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_example import template
from wealthlab.tax.projection_inputs import TaxEvent


def cash_stress():
    case = synthetic()
    end = date(2027, 1, 1)
    cover = [
        c.model_copy(
            update=dict(
                end=end,
                part_d=False,
                part_d_plan_monthly_2026=Decimal(0),
                other_monthly_health_cost_2026=Decimal(0),
            )
        )
        for c in case.medicare_plan.case.coverage
    ]
    history = [
        i.model_copy(update=dict(agi=Decimal(0), tax_exempt_interest=Decimal(0)))
        for i in case.medicare_plan.case.income_history
    ]
    medicare = case.medicare_plan.case.model_copy(
        update=dict(end_year=2027, coverage=cover, income_history=history)
    )
    plan = case.medicare_plan.model_copy(update=dict(case=medicare))
    accounts = [
        a.model_copy(update=dict(balance=Decimal(0))) if a.wrapper == "cash" else a
        for a in case.accounts
    ]
    case = case.model_copy(
        update=dict(end=end, ira_plan=None, accounts=accounts, expenses=[], medicare_plan=plan)
    )
    taxes = template(case)
    event = TaxEvent(
        date=date(2026, 3, 1),
        description="Synthetic external cash; supplied zero tax",
        cash_received=1000,
        federal=FederalIncome(),
        new_jersey=NJIncome(),
    )
    return case.model_copy(update=dict(tax_plan=taxes.model_copy(update=dict(events=[event]))))
