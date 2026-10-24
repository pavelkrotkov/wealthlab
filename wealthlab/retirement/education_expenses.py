"""Reserve annual expenses across all plans and recipients before computing tax.

An explicit allocation may reserve more than an ultimately funded withdrawal.
The unused reservation is reported, never silently transferred to another
account. This keeps expense choices reproducible when cash funding changes.
"""

from decimal import Decimal


def available_expense(item):
    if item.eligibility == "not_qualified":
        return Decimal(0)
    return item.amount - item.tax_free_aid - item.credit_expenses - item.other_vehicle_expenses


def validate_expenses(case, people):
    for item in case.expenses:
        if item.beneficiary not in people or item.paid.year != case.year:
            raise ValueError(
                "Education expenses require a known beneficiary and selected-year payment."
            )
        if item.tax_free_aid + item.credit_expenses + item.other_vehicle_expenses > item.amount:
            raise ValueError("Reserved education benefits cannot exceed the expense.")


def validate_allocations(case, accounts):
    expenses = {item.id: item for item in case.expenses}
    used = {item.id: Decimal(0) for item in case.expenses}
    allocation_keys(case, accounts)
    for item in case.allocations:
        for use in item.expenses:
            validate_use(use, expenses, accounts[item.account].beneficiary)
            used[use.expense] += use.amount
    if any(used[key] > available_expense(expenses[key]) for key in used):
        raise ValueError(
            "Education expense reused or unavailable after aid, credits and other vehicles."
        )


def validate_use(use, expenses, beneficiary):
    if use.expense not in expenses:
        raise ValueError("Unknown education expense in annual allocation.")
    if expenses[use.expense].beneficiary != beneficiary:
        raise ValueError("An education allocation cannot use another beneficiary's expense.")


def allocation_keys(case, accounts):
    keys = []
    for item in case.allocations:
        if item.account not in accounts:
            raise ValueError("Unknown education account in annual allocation.")
        keys.append(allocation_key(item, accounts))
    if len(keys) != len(set(keys)):
        raise ValueError("Supply one annual allocation per account and actual tax recipient.")
    return keys


def allocation_key(item, accounts):
    account = accounts[item.account]
    recipient = account.owner if item.recipient == "owner" else account.beneficiary
    return item.account, recipient
