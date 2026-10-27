"""Receive actual foreign refunds after original-payment/cumulative-cap validation.

Receipt-date conversion creates spending cash once. Original-credit FX is
retained in the tax record and never substituted for the cash quote. A fee
which exceeds this receipt needs a separate supported funding profile.
"""


def receive_refunds(book, wallet, start, end):
    from wealthlab.tax.foreign_credit_cash import observe
    from wealthlab.tax.foreign_tax_sources import payment_record

    for refund in sorted(book.plan.refunds, key=lambda r: (r.record.value.date, r.record.id)):
        record = payment_record(refund)
        if not start <= record.value.date < end or record.id in book.observed_ids():
            continue
        # Validate the original identity and cumulative caps before depositing cash.
        trial = book.credit_case(record.value.date.year, record.value.date, extra=[record])
        if record.fx_fee_usd > record.value.dollars():
            raise ValueError("This foreign refund profile requires cash sufficient for its fee.")
        observe(trial)
        wallet.deposit(record.value.dollars())
        if wallet.pay(record.fx_fee_usd) != record.fx_fee_usd:
            raise ValueError("A foreign refund receipt must cover its explicit cash fee.")
        book.payments.append((refund.assessment_id, record))
        book.month_records.append(record)
