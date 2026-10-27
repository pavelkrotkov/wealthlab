"""Original observed settlement records for conditional annual Spain checks."""

from wealthlab.tax.spain_example import amount


def payment(value, kind="payment", identity="paid", reverses=None):
    return dict(
        id=identity,
        owner_id="synthetic_person",
        liability_year=2025,
        tax_type="wealth",
        kind=kind,
        value=amount(value, "2026-06-20"),
        recognized_tax_eur=str(value),
        tax_recognition_source="Supplied assessment/refund tax component; cash FX remains separate",
        reverses_id=reverses,
    )
