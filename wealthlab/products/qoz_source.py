"""An actual disposal identifies eligible gain; neither proceeds nor gain are fabricated."""

from datetime import date, timedelta
from decimal import Decimal

ZERO = Decimal(0)


def source(lots, call):
    rows = [
        r
        for r in lots.book.disposals
        if r["trade_id"] == call.source_trade_id and r["lot_id"] == call.source_lot_id
    ]
    if len(rows) != 1:
        raise ValueError("A QOZ call must identify exactly one already executed source disposal.")
    row = rows[0]
    if lots.book.securities[row["security_id"]].kind != "stock":
        raise ValueError("This QOZ profile only supports direct stock capital gains.")
    sold = date.fromisoformat(row["date"])
    if sold > call.date:
        raise ValueError("QOZ cannot reinvest proceeds from a future source sale.")
    if sold.year != call.date.year:
        raise ValueError("Cross-year QOZ calls need a source-return revision profile.")
    return row, sold, sold + timedelta(days=179)


def elected_amount(row, funded, jurisdiction, treatment, used, timely):
    key = (row["trade_id"], row["lot_id"], jurisdiction)
    gain = row["federal_recognized_gain" if jurisdiction == "federal" else "nj_recognized_gain"]
    available = max(ZERO, gain - used.get(key, ZERO))
    amount = min(funded, available) if timely and treatment != "denied" else ZERO
    used[key] = used.get(key, ZERO) + amount
    return amount
