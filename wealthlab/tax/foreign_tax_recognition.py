"""Country-recognized tax may differ from actual cash and US-creditable tax.

The country engine supplies the independently recognized amount in its own
assessment currency. Actual cash is never deposited/withdrawn by these helpers;
only the single execution book changes the wallet. Refund recognition cannot
reverse more recognized local tax than the original actual payment applied.
"""

from decimal import Decimal

from wealthlab.tax.foreign_tax_translation import tax_value

ZERO = Decimal(0)


def supplied(plan):
    from wealthlab.tax.foreign_tax_validation import cash_records

    return {r.record.id: recognized(r) for r in cash_records(plan)}


def recognized(item):
    value = tax_value(item.record).amount
    return value if item.recognized_tax_native is None else item.recognized_tax_native


def amount(book, record):
    return book.recognized_native.get(record.id, tax_value(record).amount)


def validate(item, assessment):
    if tax_value(item.record).currency != assessment.currency:
        raise ValueError("Local tax recognition must retain its owning assessment currency.")
    if recognized(item) > tax_value(item.record).amount:
        raise ValueError("Recognized local tax exceeds the actual paid levy-currency amount.")
    if item.recognized_tax_native is not None and not item.recognition_source.strip():
        raise ValueError("Independent local tax recognition needs its own supplied evidence.")


def validate_refund(book, record):
    records = {r.id: r for _, r in book.payments}
    records[record.id] = record
    check_refund(record, records, book.recognized_native)


def validate_opening(plan):
    records = {r.record.id: r.record for r in plan.opening_payments}
    amounts = supplied(plan)
    for record in records.values():
        if record.kind == "refund":
            check_refund(record, records, amounts)


def check_refund(record, records, amounts):
    original = records.get(record.reverses_id)
    if original is None or original.kind == "refund":
        raise ValueError("A local tax refund requires its actual original payment identity.")
    reversed_amount = sum(
        (known_amount(r, amounts) for r in records.values() if r.reverses_id == original.id), ZERO
    )
    if reversed_amount > known_amount(original, amounts):
        raise ValueError("Refund recognition exceeds original local tax actually applied.")


def known_amount(record, amounts):
    return amounts.get(record.id, tax_value(record).amount)
