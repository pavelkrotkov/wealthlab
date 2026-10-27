"""Native preferential/decree tax uses actual US tax paid and explicit credit treatment.

Denied credit keeps the same receipts/bases/economics. Allowed credit reuses
the existing native NIIT, mixed-source and different-basis guards; no gross
ratio invents a preferential credit that the native model does not support.
"""

from decimal import Decimal

from wealthlab.tax.pr_execution_gain_credit import complete_mixed
from wealthlab.tax.pr_execution_gains import local
from wealthlab.tax.pr_incentive_candidate import federal_rows, paid_tax
from wealthlab.tax.pr_incentive_credit_guards import credit
from wealthlab.tax.pr_preferential import calculate
from wealthlab.tax.pr_recognition import recognized

ZERO = Decimal(0)


def assess(annual, case, statuses, us, actual):
    chosen = selected(annual, case, statuses, us, actual)
    profile = annual.pr_federal.gain_profile
    if profile.treatment != "incentive":
        return chosen
    ordinary_profile = profile.model_copy(update=dict(treatment="ordinary"))
    context = annual.pr_federal.model_copy(update=dict(gain_profile=ordinary_profile))
    ordinary = annual.model_copy(update=dict(pr_federal=context))
    try:
        alternative = selected(ordinary, case, statuses, us, actual)
    except ValueError as error:
        return dict(chosen, ordinary_alternative_unresolved=str(error))
    if alternative["assessment"]["income_tax"] < chosen["assessment"]["income_tax"]:
        return dict(
            alternative,
            selected_treatment="more_favorable_ordinary",
            requested_treatment="incentive",
        )
    return chosen


def selected(annual, case, statuses, us, actual):
    native, slices, audit = local(annual, case)
    derived = case.model_copy(update=dict(income=[s.row for s in slices]))
    taxable = federal_rows(derived, statuses)
    local_rows = recognized(derived)
    local_slices = [s for s in slices if s.row in local_rows]
    supplied = annual.pr_federal.gain_profile
    eligible = paid_credit(supplied.local_us_credit_treatment, us, actual, taxable, local_slices)
    result = calculate(derived, local_slices, eligible)
    return dict(
        assessment=result,
        creditable_us_tax_after_federal_credit=eligible,
        actual_us_income_tax_paid=actual,
        federal_foreign_credit=us["foreign_tax_credit"],
        payroll_excluded=us["employee_payroll"],
        niit_excluded=us["niit"],
        source_year=annual.policy.year,
        gain_allocations=audit,
        local_us_credit_treatment=supplied.local_us_credit_treatment,
        selected_treatment=supplied.treatment,
        decree=native.decree.model_dump(mode="json"),
    )


def paid_credit(treatment, us, actual, taxable, slices):
    if treatment == "unresolved":
        raise ValueError("PR paid-US-tax preferential credit treatment is unresolved.")
    if treatment == "denied" or actual == 0:
        return ZERO
    if complete_mixed(taxable, slices, us):
        return min(actual, us["income_tax"])
    credit(slices, us)
    paid = dict(us, income_tax=min(actual, us["income_tax"]))
    return paid_tax(paid, taxable, slices)
