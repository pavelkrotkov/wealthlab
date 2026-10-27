"""Require coherent annual identities and dates before applying supplied fiscal facts."""

from wealthlab.tax.spain_payment_validation import validate_payments
from wealthlab.tax.spain_wealth_validation import validate as validate_wealth


def validate(case):
    if case.year != 2025 and case.policy != "frozen_2025":
        raise ValueError("Only 2025 is published policy; later years require explicit frozen law.")
    validate_identity(case)
    for income in case.incomes:
        validate_income(case.year, income)
    validate_wealth(case)
    validate_payments(case)


def validate_identity(case):
    records = [*case.incomes, *case.assets, *case.debts, *case.payments]
    if len({r.id for r in records}) != len(records):
        raise ValueError("Spanish source record identifiers must be unique.")
    if any(r.owner_id != case.person_id for r in records):
        raise ValueError("Every record belongs to the case person; enter that person's share.")


def validate_income(year, income):
    received = income.amount if income.kind == "income" else income.proceeds
    if received.date.year != year:
        raise ValueError("Income/disposal translation must have a date in the liability year.")
    if income.kind == "disposal":
        if income.acquisition.date > received.date:
            raise ValueError("A disposal cannot precede its separately translated acquisition.")
        if min(income.proceeds.amount, income.acquisition.amount) < 0:
            raise ValueError("Disposal and acquisition prices must be nonnegative.")
