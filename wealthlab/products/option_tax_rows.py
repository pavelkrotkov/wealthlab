"""Recognition and tax character do not create a cash receipt or tax benefit."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.option_tax import unresolved


def tax_row(key, day, jurisdiction, amount, deferral, long_fraction, errors):
    if deferral > max(Decimal(0), -amount):
        raise ValueError("Supplied option deferral exceeds the actual loss.")
    recognized = amount + deferral
    long = money(recognized * long_fraction)
    return dict(
        id=key,
        date=day,
        jurisdiction=jurisdiction,
        economic_gain=amount,
        deferred=deferral,
        recognized=None if errors else recognized,
        short_term=None if errors or jurisdiction == "nj" else recognized - long,
        long_term=None if errors or jurisdiction == "nj" else long,
        unresolved=errors,
    )


def stock_recognition(state):
    result = []
    for row in state.book.disposals:
        for jurisdiction in ("federal", "nj"):
            errors = unresolved(state.case.tax, jurisdiction)
            amount = row[f"{jurisdiction}_gross_gain"]
            key = row["trade_id"] + ":" + row["lot_id"]
            deferral = getattr(state.case.tax, f"{jurisdiction}_deferrals").get(key, Decimal(0))
            fraction = Decimal(row["federal_character"] == "long_term")
            result.append(
                tax_row(key, row["date"], jurisdiction, amount, deferral, fraction, errors)
            )
    return result
