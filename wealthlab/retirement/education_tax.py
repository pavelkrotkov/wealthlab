"""Annual account/recipient tax ingredients; expense allocation is explicit, never duplicated.

Post-2014 QTP account aggregation was eliminated. Each account's distributed
earnings stay with that account and actual recipient, including when the owner
is also the beneficiary. Expense reservations span all accounts. Their annual
payment may follow a distribution, but it never supplies earlier cash funding.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.retirement.education_expenses import allocation_key, available_expense
from wealthlab.retirement.education_nj import deduction, recapture_income


def reconcile(case, book):
    groups = distribution_groups(book["rows"])
    allocations = {allocation_key(a, book["accounts"]): a for a in case.allocations}
    if allocations.keys() - groups.keys():
        raise ValueError("Annual allocation requires a withdrawal for its account and recipient.")
    rows = [group_tax(book, key, entries, allocations.get(key)) for key, entries in groups.items()]
    reserved = {e.id: Decimal(0) for e in case.expenses}
    for allocation in case.allocations:
        for use in allocation.expenses:
            reserved[use.expense] += use.amount
    return dict(
        annual_tax_groups=rows,
        njbest_funded_contributions=book["nj_contributions"],
        njbest_potential_deduction=deduction(case.nj_gross_income, book["nj_contributions"]),
        federal_contribution_deduction=Decimal(0),
        unallocated_expenses={e.id: available_expense(e) - reserved[e.id] for e in case.expenses},
        sources=[
            "https://www.irs.gov/publications/p970",
            "https://www.nj.gov/treasury/taxation/individuals/collegededuction.shtml",
            "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf",
        ],
    )


def distribution_groups(rows):
    groups = {}
    for row in rows:
        if row["kind"] == "withdrawal":
            key = row["account"], row["recipient"]
            groups.setdefault(key, []).append(row)
    return groups


def group_tax(book, key, entries, allocation):
    gross = sum(row["funded"] for row in entries)
    earnings = sum(row["earnings"] for row in entries)
    principal = gross - earnings
    allocated = allocated_amount(allocation)
    qualified = min(gross, allocated)
    taxable = money(earnings * (gross - qualified) / gross) if gross else Decimal(0)
    exception = allocation.additional_tax_exempt_earnings if allocation else Decimal(0)
    if exception > taxable:
        raise ValueError("Conditional additional-tax exception exceeds actual taxable earnings.")
    nonqualified_basis = money(principal * (gross - qualified) / gross) if gross else Decimal(0)
    nj = recapture_income(book, key[0], allocation, nonqualified_basis, taxable, qualified == gross)
    return dict(
        account=key[0],
        recipient=entries[0]["recipient"],
        gross_distribution=gross,
        returned_principal=principal,
        distributed_earnings=earnings,
        qualified_expenses_used=qualified,
        reserved_but_unused_expenses=allocated - qualified,
        federal_taxable_earnings=taxable,
        conditional_exempt_earnings=exception,
        federal_additional_tax=money((taxable - exception) * Decimal(".10")),
        **nj,
    )


def allocated_amount(allocation):
    if allocation is None:
        return Decimal(0)
    return sum((use.amount for use in allocation.expenses), Decimal(0))
