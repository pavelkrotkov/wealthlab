"""Refunds preserve original tax identity and cannot erase more tax than was paid.

The original taxpayer, country, tax kind, liability year and eligibility are
retained. Cash and creditable reversals have separate cumulative caps; their
FX values may differ without changing either original native amount. Interest
or unrelated receipts need their own income classification outside this profile.
"""

from decimal import Decimal

from wealthlab.tax.foreign_tax_translation import tax_value

ZERO = Decimal(0)


def validate_refund(refund, records):
    original = records.get(refund.reverses_id)
    if original is None or original.kind == "refund":
        raise ValueError("A refund must identify an observed original tax payment/withholding.")
    validate_refund_identity(refund, original)
    validate_refund_amounts(original, records)


def validate_refund_identity(refund, original):
    keys = ("owner_id", "country", "tax_type", "basket", "liability_year", "eligibility")
    if any(getattr(refund, key) != getattr(original, key) for key in keys):
        raise ValueError(
            "A refund must retain the original taxpayer, jurisdiction, tax and basket."
        )
    if (
        refund.value.date < original.value.date
        or tax_value(refund).currency != tax_value(original).currency
    ):
        raise ValueError("Refund timing/currency must reconcile to its original payment.")


def validate_refund_amounts(original, records):
    reversals = [r for r in records.values() if r.reverses_id == original.id]
    if sum((tax_value(r).amount for r in reversals), ZERO) > tax_value(original).amount:
        raise ValueError(
            "Refund cash exceeds its original native payment; separate other receipts."
        )
    if sum((r.creditable_native for r in reversals), ZERO) > original.creditable_native:
        raise ValueError("A refund cannot reverse more creditable tax than originally observed.")
