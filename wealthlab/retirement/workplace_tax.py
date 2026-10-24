"""Exclude only funded pretax elections from income-tax wages, preserving payroll.

The federal adapter receives taxable wages plus pencon deferrals so its
payroll base still includes the elected amount. Roth elections stay in wages.
The same adjusted wage streams determine entered withholding percentages.
"""

from decimal import Decimal

ZERO = Decimal(0)


def events(members, excluded, when):
    from wealthlab.tax.facts import FederalIncome
    from wealthlab.tax.nj_facts import NJIncome
    from wealthlab.tax.projection_inputs import TaxEvent

    fields = {
        f"deferrals_{'primary' if i == 0 else 'spouse'}": excluded[p] for i, p in enumerate(members)
    }
    return (
        TaxEvent(
            date=when,
            description="Funded pretax employee 401(k) deferrals",
            cash_received=0,
            federal=FederalIncome(**fields),
            new_jersey=NJIncome(),
        ),
    )


def tax_amounts(amounts, rules, members, excluded):
    adjusted = dict(amounts)
    for i, owner in enumerate(members):
        field = "wages_primary" if i == 0 else "wages_spouse"
        left = excluded[owner]
        for r in [r for r in rules if r.federal == field]:
            take = min(left, adjusted[r.income_id])
            adjusted[r.income_id] -= take
            left -= take
    return adjusted


def summarize(rows):
    return dict(
        workplace_contributions=sum((r["funded"] for r in rows), ZERO),
        workplace_pretax=sum((r["funded"] for r in rows if r["kind"] == "pretax_401k"), ZERO),
        workplace_unfilled=sum((r["requested"] - r["funded"] for r in rows), ZERO),
    )
