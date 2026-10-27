"""Revised credit facts preserve original tax cash, dates and payment FX.

Only actual later-year refunds reduce an original paid-year credit. Same-year
refund rows remain part of that year's cash history. No future receipt is
backdated into an old return or treated as new spending cash there.
"""

from datetime import date
from decimal import Decimal

from wealthlab.tax.foreign_credit_facts import ForeignCredits

ZERO = Decimal(0)


def original_case(book, annual, when):
    year = annual.policy.year
    case = book.credit_case(
        year,
        date(year, 12, 31),
        annual=annual.model_copy(update=dict(foreign_credits=ForeignCredits())),
    )
    refunds = {}
    for _, record in book.payments:
        if record.kind == "refund" and year < record.value.date.year and record.value.date <= when:
            refunds[record.reverses_id] = (
                refunds.get(record.reverses_id, ZERO) + record.creditable_native
            )
    records = [
        record.model_copy(
            update=dict(creditable_native=record.creditable_native - refunds.get(record.id, ZERO))
        )
        for record in case.tax_cash
    ]
    if any(record.creditable_native < 0 for record in records):
        raise ValueError("Actual later refunds cannot reverse more original creditable tax.")
    return case.model_copy(update=dict(tax_cash=records))


def pending(book, when):
    records = {record.id: record for _, record in book.payments}
    result = []
    for record in records.values():
        if not requires_revision(book, record):
            continue
        original = records[record.reverses_id]
        if original.value.date.year < when.year:
            result.append((record, original.value.date.year))
    return result


def requires_revision(book, record):
    return (
        record.kind == "refund"
        and record.tax_type == "income"
        and record.creditable_native > 0
        and record.eligibility == "allowed"
        and record.value.date >= book.projection_start
        and record.id not in book.redetermined_refunds
    )
