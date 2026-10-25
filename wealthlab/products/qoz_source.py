"""Only actual direct-stock disposal rows supply eligible source gain.

A mandatory deemed QOF inclusion creates no new trade and cannot refresh used
gain. The 180-day clock includes the sale date; a tax-year boundary does not
create a fresh clock. Both source proceeds and the eventual investment remain
actual cash movements in their existing household books.
"""

from datetime import date, timedelta
from decimal import Decimal

ZERO = Decimal(0)


def source(lots, call, allow_prior_year=False):
    rows = [
        r
        for r in lots.book.disposals
        if r["trade_id"] == call.source_trade_id and r["lot_id"] == call.source_lot_id
    ]
    if len(rows) != 1:
        raise ValueError("A QOZ call must identify exactly one already executed source disposal.")
    row = rows[0]
    sold = date.fromisoformat(row["date"])
    validate_source(lots, row, sold, call, allow_prior_year)
    return row, sold, sold + timedelta(days=179)


def validate_source(lots, row, sold, call, allow_prior_year):
    """Accept only observed stock disposals and explicitly supported original tax years."""
    if lots.book.securities[row["security_id"]].kind != "stock":
        raise ValueError("This QOZ profile only supports direct stock capital gains.")
    if sold > call.date:
        raise ValueError("QOZ cannot reinvest proceeds from a future source sale.")
    if sold.year != call.date.year and not allow_prior_year:
        raise ValueError("Cross-year QOZ calls need a source-return revision profile.")
    if sold.year < call.date.year - 1:
        raise ValueError("QOZ supports only current or immediately prior actual source years.")


def elected_amount(row, funded, jurisdiction, treatment, used, timely):
    key = (row["trade_id"], row["lot_id"], jurisdiction)
    gain = row["federal_recognized_gain" if jurisdiction == "federal" else "nj_recognized_gain"]
    available = max(ZERO, gain - used.get(key, ZERO))
    amount = min(funded, available) if timely and treatment != "denied" else ZERO
    used[key] = used.get(key, ZERO) + amount
    return amount
