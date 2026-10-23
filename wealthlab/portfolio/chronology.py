"""Opening positions exist already; dated trades cannot enter the ledger retroactively.

A buy's ID also identifies the lot it creates. Disallowing collisions with all
opening lots prevents ID reuse even if an earlier trade has fully sold that lot.
Same-day orders retain their input order; no hidden reordering chooses tax lots.
"""


def validate_dates(case):
    validate_order(case)
    validate_purchase_ids(case)
    if case.end < case.as_of:
        raise ValueError("Closing valuation date cannot precede the opening date.")
    if any(lot.acquired > case.as_of for lot in case.lots):
        raise ValueError("Opening lots must already exist at the opening date.")
    if any(not case.as_of <= trade.date <= case.end for trade in case.trades):
        raise ValueError("Trades must lie inside the opening/closing dates.")


def validate_order(case):
    dates = [trade.date for trade in case.trades]
    if dates != sorted(dates):
        raise ValueError("Trades must be ordered by date; same-day list order controls execution.")


def validate_purchase_ids(case):
    opening = {lot.id for lot in case.lots}
    if any(trade.action == "buy" and trade.id in opening for trade in case.trades):
        raise ValueError(
            "A purchase trade ID becomes its lot ID and must not collide with opening lots."
        )
