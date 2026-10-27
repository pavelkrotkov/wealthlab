"""A linked gross/net receipt credits actual foreign tax without another wallet debit."""


def observe(book, ledger, start, end):
    from wealthlab.tax.foreign_tax_sources import payment_record

    templates = {r.record.id: r for r in book.plan.source_withholding}
    validate_unique_receipts(ledger.source_receipts)
    for receipt in ledger.source_receipts:
        identity = receipt.get("foreign_payment_id")
        if identity is None:
            continue
        if identity not in templates:
            raise ValueError(
                "Foreign source withholding needs its exact assessment/payment record."
            )
        item = templates[identity]
        record = payment_record(item)
        validate_receipt(record, receipt)
        if not start <= record.value.date < end:
            raise ValueError("Foreign withholding date must belong to its actual receipt month.")
        if identity not in book.observed_ids():
            book.payments.append((item.assessment_id, record))
            book.month_records.append(record)


def validate_receipt(record, receipt):
    if (
        record.value.date.isoformat() != receipt["date"]
        or record.value.dollars() != receipt["foreign_tax_withheld"]
        or record.fx_fee_usd
    ):
        raise ValueError("Foreign withholding must reconcile the actual dated gross/net receipt.")


def validate_unique_receipts(receipts):
    ids = [r["foreign_payment_id"] for r in receipts if r.get("foreign_payment_id")]
    if len(ids) != len(set(ids)):
        raise ValueError("A foreign payment cannot credit two actual source receipts.")
