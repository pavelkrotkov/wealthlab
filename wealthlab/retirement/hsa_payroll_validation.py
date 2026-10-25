"""Validate payroll eligibility and shared HSA context before any wage exclusion.

This bounded profile uses first-day monthly orders and gross W2 streams. It
excludes partners, ineligible S-corporation owners, unknown other payroll
reductions and ordinary after-tax payroll deductions. Monthly cash pooling
is explicit; a later dated receipt cannot manufacture current owner wages.
"""

from wealthlab.retirement.hsa_validation import validate_destination
from wealthlab.retirement.workplace_wages import validate_wages


def validate(scenario):
    plan = scenario.hsa_plan.payroll
    if plan is None:
        return
    if not all(
        (
            plan.qualifying_section125_w2_employee_confirmed,
            plan.gross_wages_before_salary_reduction_confirmed,
            plan.complete_elections_and_no_other_payroll_reductions_confirmed,
        )
    ):
        raise ValueError(
            "Confirm qualifying section125 employees, gross wages and complete payroll elections."
        )
    validate_wages(scenario)
    validate_ids(scenario)
    for order in plan.orders:
        validate_order(order, scenario)


def validate_ids(scenario):
    plan = scenario.hsa_plan
    rows = [
        *plan.medical_receipts,
        *plan.contributions,
        *plan.withdrawals,
        *plan.interest,
        *plan.medical_bills,
        *scenario.accounts,
        *scenario.members,
    ]
    occupied = {r.id for r in rows}
    identities = [r.id for r in plan.payroll.orders]
    if len(identities) != len(set(identities)) or set(identities) & occupied:
        raise ValueError("Payroll HSA order IDs must be unique and distinct from HSA context.")


def validate_order(order, scenario):
    if order.provenance == "unresolved":
        raise ValueError("Resolve payroll HSA order assumptions.")
    if order.date.day != 1 or not scenario.start <= order.date < scenario.end:
        raise ValueError("Payroll HSA orders require first-day dates inside the projection.")
    validate_account(order, scenario)


def validate_account(order, scenario):
    accounts = {a.id: a for a in scenario.accounts if a.wrapper == "hsa"}
    context = next(y for y in scenario.hsa_plan.years if y.year == order.date.year)
    owners = {p.id: p for p in context.owners}
    validate_destination(order.destination, order.date, accounts, owners)
    if accounts[order.destination].owner != order.owner:
        raise ValueError("Payroll HSA owner must match the individual account owner.")
