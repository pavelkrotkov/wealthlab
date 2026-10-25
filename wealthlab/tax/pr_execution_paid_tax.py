"""PR credit ordering uses remaining native US income tax and observed payments.

Employee payroll and NIIT never enter this ordinary PR credit base. An unpaid
payroll balance has no supplied income/payroll payment allocation, so that case
is withheld rather than assigning every dollar to the more favorable tax.
"""

from decimal import Decimal

from wealthlab.tax.pr_candidate import paid_us_tax
from wealthlab.tax.pr_execution_context import prepare
from wealthlab.tax.pr_local import calculate
from wealthlab.tax.pr_recognition import recognized
from wealthlab.tax.pr_residence import excluded

ZERO = Decimal(0)


def evaluate(position):
    annual, us = position.case, position.result["federal"]
    case, statuses = prepare(annual)
    rows = recognized(case)
    taxable = [
        row
        for row in case.income
        if not excluded(row, getattr(case, row.owner), statuses[row.owner], annual.policy.year)
    ]
    actual = actual_income_tax(position)
    # Reuse the native allocation with NIIT unchanged; substitute actual paid
    # ordinary income tax only after federal credits have reduced the liability.
    ordinary = min(actual, max(ZERO, us["income_tax"] - us["niit"]))
    paid_result = dict(us, income_tax=ordinary + us["niit"])
    creditable = paid_us_tax(paid_result, taxable, rows)
    return dict(
        actual_net_federal_paid=position.net_paid["federal"],
        actual_us_income_tax_paid=actual,
        creditable_us_tax_after_federal_credit=creditable,
        assessment=calculate(case, rows, creditable),
        source_year=annual.policy.year,
        federal_foreign_credit=us["foreign_tax_credit"],
        payroll_excluded=us["employee_payroll"],
        niit_excluded=us["niit"],
    )


def actual_income_tax(position):
    payments, federal = position.case.payments, position.result["federal"]
    if payments.employee_payroll_withheld != federal["employee_payroll"]:
        raise ValueError(
            "PR paid-US-tax credit needs a confirmed income/payroll payment allocation."
        )
    income = payments.federal_income_withheld + payments.federal_estimates
    initial_total = income + payments.employee_payroll_withheld
    net = income + position.net_paid["federal"] - initial_total
    if net < 0:
        raise ValueError("US refund allocation cannot reduce income tax below zero.")
    return net
