"""Keep original employee payroll once while replacing income-tax jurisdictions."""

from decimal import Decimal

from wealthlab.tax.pr_federal import calculate as federal
from wealthlab.tax.pr_local import calculate as local
from wealthlab.tax.pr_recognition import recognized
from wealthlab.tax.pr_residence import excluded


def candidate(case, baseline, statuses):
    year = case.baseline.policy.year
    taxable = [
        row
        for row in case.income
        if not excluded(row, getattr(case, row.owner), statuses[row.owner], year)
    ]
    foreign = [row for row in taxable if row.federal_source == "PR"]
    us = federal(case, taxable, foreign)
    rows = recognized(case)
    creditable_us = paid_us_tax(us, taxable, rows)
    pr = local(case, rows, creditable_us)
    if case.pr_income_tax_paid_for_us_credit > pr["income_tax"]:
        raise ValueError("Claimed current-year PR paid tax exceeds computed PR liability.")
    payroll = baseline["federal"]["employee_payroll"]
    us.update(
        employee_payroll=payroll,
        additional_medicare=baseline["federal"]["additional_medicare"],
        total=us["income_tax"] + payroll,
    )
    total = us["income_tax"] + pr["income_tax"] + payroll
    return dict(
        federal=us,
        puerto_rico=pr,
        employee_payroll=payroll,
        federal_pr_payroll_total=total,
        comparable_mainland_federal_payroll=baseline["federal"]["total"],
        federal_pr_difference=total - baseline["federal"]["total"],
        conditional=conditional(case, statuses),
        excluded_federal=sum(row.federal_amount for row in case.income) - us["taxable_gross"],
        recognized_pr_rows=[row.model_dump(mode="json") for row in rows],
    )


def paid_us_tax(us, taxable, recognized_rows):
    # Schedule C Part III reduces paid US tax for US-taxable income excluded
    # locally. The foreign-source limitation is applied separately in local().
    gross = sum((row.federal_amount for row in taxable), Decimal(0))
    eligible = sum((row.federal_amount for row in taxable if row in recognized_rows), Decimal(0))
    ratio = eligible / gross if gross else Decimal(0)
    return (us["income_tax"] - us["niit"]) * ratio


def conditional(case, statuses):
    return (
        any(status["conditional"] for status in statuses.values())
        or case.pr_wages_reported_on_form_499r2 == "assumed"
    )
