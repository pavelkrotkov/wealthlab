"""Keep qualified reimbursements distinct from future bills and duplicate tax inputs.

This initial household profile uses confirmed receipts already paid before
the projection. It cannot make an unpaid future expense qualify merely by
naming it. Employer funding and personal deposits share actual annual room;
manual deductions and generic transfers cannot introduce them again.
"""

from wealthlab.retirement.hsa_household_tax import validate as validate_distributions


def validate_sources(scenario):
    plan = scenario.hsa_plan
    accounts = {a.id for a in scenario.accounts if a.wrapper == "hsa"}
    if not accounts:
        raise ValueError("Supply an explicitly confirmed cash HSA account.")
    if any(c.destination in accounts for c in scenario.contributions):
        raise ValueError("Remove generic transfers into the HSA cash book.")
    validate_receipts(plan, scenario.start)
    validate_manual_tax(scenario)
    validate_bills(scenario)


def validate_receipts(plan, start):
    if any(r.paid >= start for r in plan.medical_receipts):
        raise ValueError("This HSA reimbursement profile uses receipts paid before the projection.")
    validate_distributions(plan)
    records = [
        *plan.medical_receipts,
        *plan.contributions,
        *plan.withdrawals,
        *plan.interest,
        *plan.medical_bills,
    ]
    if len({r.id for r in records}) != len(records):
        raise ValueError("Household HSA event and receipt IDs must be unique.")


def validate_manual_tax(scenario):
    incomes = [c.federal_income for c in scenario.tax_plan.cases]
    incomes += [e.federal for e in scenario.tax_plan.events]
    if any(i.deductible_hsa_contributions for i in incomes):
        raise ValueError("Remove manual HSA deductions when generating funded HSA contributions.")
    records = [
        *scenario.hsa_plan.contributions,
        *scenario.hsa_plan.withdrawals,
        *scenario.hsa_plan.interest,
    ]
    if any(not scenario.start <= r.date < scenario.end for r in records):
        raise ValueError("HSA cash events must lie inside the household projection.")


def validate_bills(scenario):
    plan = scenario.hsa_plan
    if plan.medical_bills and not plan.bill_expenses_excluded_from_other_inputs_confirmed:
        raise ValueError(
            "Confirm net medical bills are excluded from other budgets, receipts "
            "and deductions; their cash-paid portions remain undeducted."
        )
    accounts = {a.id for a in scenario.accounts if a.wrapper == "hsa"}
    for bill in plan.medical_bills:
        validate_bill(bill, scenario, accounts)


def validate_bill(bill, scenario, accounts):
    if not scenario.start <= bill.date < scenario.end:
        raise ValueError("New medical bills must fall inside the household projection.")
    if bill.hsa_source is not None and bill.hsa_source not in accounts:
        raise ValueError("Medical direct payments require a known household HSA source.")
