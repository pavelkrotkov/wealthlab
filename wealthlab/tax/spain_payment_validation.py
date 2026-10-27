"""A settlement keeps its liability year, cash date and original payment identity."""


def validate_payments(case):
    payments = {p.id: p for p in case.payments}
    for payment in case.payments:
        validate_dates(case, payment)
        validate_origin(payment, payments, case.payments)


def validate_dates(case, payment):
    if payment.value.amount < 0 or payment.value.date > case.as_of:
        raise ValueError("Tax payments need observed nonnegative cash by the as-of date.")
    if payment.liability_year != case.year:
        raise ValueError("Payment liability year must match this annual assessment.")


def validate_origin(payment, payments, records):
    if payment.kind == "refund":
        original = payments.get(payment.reverses_id)
        if original is None or original.kind == "refund":
            raise ValueError("A refund must identify its original payment or withholding.")
        validate_refund(payment, original, records)
    elif payment.reverses_id is not None:
        raise ValueError("Only a refund can reverse a prior payment.")


def validate_refund(refund, original, payments):
    if original.tax_type != refund.tax_type or original.value.date > refund.value.date:
        raise ValueError("A refund must follow a payment of the same tax type.")
    reversed_tax = sum(p.recognized_tax_eur for p in payments if p.reverses_id == original.id)
    if reversed_tax > original.recognized_tax_eur:
        raise ValueError("Refunds cannot reverse more recognized tax than the original payment.")
