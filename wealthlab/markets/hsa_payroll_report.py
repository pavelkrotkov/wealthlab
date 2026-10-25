"""HSA policy outcomes distinguish requested payroll from actual personal funding."""

from decimal import Decimal

ZERO = Decimal(0)


def summary(scenario, rows):
    if scenario.hsa_plan is None:
        return {}
    accounts = {a.id for a in scenario.accounts if a.wrapper == "hsa"}
    return dict(
        hsa_salary_reductions=total(rows, "hsa_payroll_contributions"),
        hsa_salary_elections_unfilled=total(rows, "hsa_payroll_unfilled"),
        hsa_personal_deposits=total(rows, "hsa_personal_contributions"),
        hsa_external_employer_funding=total(rows, "hsa_employer_funding"),
        hsa_ending_gross_assets=sum((rows[-1]["account_balances"][a] for a in accounts), ZERO),
    )


def total(rows, field):
    return sum((r.get(field, ZERO) for r in rows), ZERO)
