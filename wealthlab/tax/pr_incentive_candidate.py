"""Separate ordinary and conditional incentive calculations on the same derived source slices."""

from decimal import Decimal

from wealthlab.tax.pr_candidate import conditional
from wealthlab.tax.pr_federal import calculate as federal
from wealthlab.tax.pr_incentive_credit_guards import credit
from wealthlab.tax.pr_inputs import income
from wealthlab.tax.pr_preferential import calculate as local
from wealthlab.tax.pr_recognition import recognized
from wealthlab.tax.pr_residence import excluded
from wealthlab.tax.pr_tax_slices import prepare


def calculate(comparison, baseline, statuses, *, incentivized=False):
    slices, gains = prepare(comparison, incentivized=incentivized)
    annual = comparison.annual.model_copy(update={"income": [item.row for item in slices]})
    taxable = federal_rows(annual, statuses)
    foreign = [row for row in taxable if row.federal_source == "PR"]
    us = federal(annual, taxable, foreign)
    local_rows = recognized(annual)
    local_slices = [item for item in slices if item.row in local_rows]
    credit(local_slices, us)
    paid = paid_tax(us, taxable, local_slices)
    pr = local(annual, local_slices, paid)
    payroll = baseline["federal"]["employee_payroll"]
    us.update(
        employee_payroll=payroll,
        additional_medicare=baseline["federal"]["additional_medicare"],
        total=us["income_tax"] + payroll,
    )
    total = us["income_tax"] + pr["income_tax"] + payroll
    if annual.pr_income_tax_paid_for_us_credit > pr["income_tax"]:
        raise ValueError("Current-year PR paid-tax credit exceeds calculated PR liability.")
    return dict(
        federal=us,
        puerto_rico=pr,
        employee_payroll=payroll,
        federal_pr_payroll_total=total,
        conditional=gain_conditional(comparison, statuses),
        gain_allocations=gains,
        derived_income=income(annual.income).model_dump(mode="json"),
        recognized_slices=[
            dict(row=item.row.model_dump(mode="json"), treatment=item.treatment)
            for item in local_slices
        ],
    )


def federal_rows(annual, statuses):
    year = annual.baseline.policy.year
    return [
        row
        for row in annual.income
        if not excluded(row, getattr(annual, row.owner), statuses[row.owner], year)
    ]


def paid_tax(us, taxable, local_slices):
    eligible = [item.row for item in local_slices if item.treatment in {"ordinary", "lt15"}]
    # Part III of Schedule C excludes federal tax allocated to locally exempt
    # amounts. Act60 special-rate credits are guarded before this ordinary limit.
    gross = sum((row.federal_amount for row in taxable), Decimal(0))
    counted = sum((row.federal_amount for row in taxable if row in eligible), Decimal(0))
    return (us["income_tax"] - us["niit"]) * counted / gross if gross else Decimal(0)


def gain_conditional(comparison, statuses):
    return conditional(comparison.annual, statuses) or any(
        "assumed" in asset.model_dump().values() for asset in comparison.gains
    )
