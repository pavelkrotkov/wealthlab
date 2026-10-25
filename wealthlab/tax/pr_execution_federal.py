"""Use the prepared PR exclusion/proration policy and native federal credit order once."""

from wealthlab.tax import federal
from wealthlab.tax.facts import Deductions
from wealthlab.tax.pr_execution_context import prepare
from wealthlab.tax.pr_federal import calculate as prepared_federal
from wealthlab.tax.pr_residence import excluded


def calculate(annual):
    case, statuses = prepare(annual)
    taxable = [
        row
        for row in case.income
        if not excluded(row, getattr(case, row.owner), statuses[row.owner], annual.policy.year)
    ]
    result = prepared_federal(case, taxable, [], native_credits=annual.foreign_credits)
    worldwide = federal.calculate(annual.filing, annual.federal_income, Deductions(), annual.policy)
    payroll = worldwide["employee_payroll"]
    result.update(
        employee_payroll=payroll,
        additional_medicare=worldwide["additional_medicare"],
        total=result["income_tax"] + payroll,
        pr_residence=statuses,
        pr_source_inputs=annual.pr_federal.model_dump(mode="json"),
        pr_excluded_income=result["worldwide_gross"] - result["taxable_gross"],
    )
    return result
