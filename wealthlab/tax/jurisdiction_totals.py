"""Read final native tax books without recalculating tax or moving household cash.

Assessed amounts keep their levy currency. Bank payments, actual refunds and
recorded payment fees keep their cash-date USD values. Opening payments belong
to the supplied books; a credit is already in the native liability, never cash.
"""

from decimal import Decimal

from wealthlab.tax.foreign_tax_redetermination_reporting import finish as foreign_finish
from wealthlab.tax.foreign_tax_translation import tax_value
from wealthlab.tax.return_positions import capture, liabilities

ZERO = Decimal(0)
LABELS = {"federal": "US federal", "new_jersey": "New Jersey"}


def finish(ledger, rows):
    foreign_finish(ledger, rows)
    if ledger is not None:
        rows[-1]["jurisdiction_totals"] = summarize(ledger, rows[-1])


def summarize(ledger, row):
    groups = {}
    domestic(groups, ledger)
    if ledger.foreign is not None:
        foreign(groups, ledger.foreign, row)
    result = []
    for key in sorted(groups):
        total = groups[key]
        total["assessment_status"] = ", ".join(sorted(total.pop("statuses"))) or "not observed"
        total["net_cash_usd"] = (
            total["paid_usd"] - total["refunded_usd"] + total["payment_fees_usd"]
        )
        result.append(total)
    return result


def bucket(groups, jurisdiction, currency):
    return groups.setdefault(
        (jurisdiction, currency),
        dict(
            jurisdiction=jurisdiction,
            currency=currency,
            assessed_native=ZERO,
            paid_usd=ZERO,
            refunded_usd=ZERO,
            payment_fees_usd=ZERO,
            statuses=set(),
        ),
    )


def domestic(groups, ledger):
    positions = dict(ledger.closed_returns)
    positions.setdefault(ledger.case.policy.year, capture(ledger.case, ledger.result))
    for year, position in positions.items():
        for jurisdiction, assessed in liabilities(position.result).items():
            total = bucket(groups, LABELS[jurisdiction], "USD")
            total["assessed_native"] += assessed
            total["paid_usd"] += position.net_paid[jurisdiction]
            total["statuses"].add(return_status(ledger, year))
    for receipt in ledger.refund_receipts:
        for jurisdiction, amount in receipt["components"].items():
            total = bucket(groups, LABELS[jurisdiction], "USD")
            total["refunded_usd"] += amount
            if receipt.get("source_year") in positions:
                # Closed-return net paid has already subtracted this actual refund.
                total["paid_usd"] += amount


def return_status(ledger, year):
    if year in ledger.provisional_returns:
        return "provisional"
    return "closed" if year in ledger.closed_returns else "partial"


def foreign(groups, book, row):
    for position in row.get("foreign_tax_positions", []):
        total = bucket(groups, position["country"], position["currency"])
        total["assessed_native"] += position["assessed_native"]
        total["statuses"].add(position["assessment_status"])
    for _, record in book.payments:
        total = bucket(groups, record.country, tax_value(record).currency)
        field = "refunded_usd" if record.kind == "refund" else "paid_usd"
        total[field] += record.value.dollars()
        total["payment_fees_usd"] += record.fx_fee_usd
