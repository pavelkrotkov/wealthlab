"""Report recognized versus pending federal losses without spending future tax benefits."""

from datetime import date, timedelta
from decimal import Decimal


def finish_row(row, book, end):
    taxable = book.accounts[row["account_id"]].wrapper == "taxable"
    unresolved = row["wash_unmatched_quantity"] and end < date.fromisoformat(
        row["date"]
    ) + timedelta(days=30)
    adjusted = row["federal_gross_gain"] + row["federal_wash_disallowed"]
    row["federal_recognized_gain"] = adjusted if taxable and not unresolved else Decimal(0)
    row["federal_pending_loss"] = -adjusted if taxable and unresolved else Decimal(0)
    row["federal_status"] = "pending wash window" if unresolved else "modeled federal recognition"
    row["nj_status"] = "Unadjusted NJ gain; no NJ wash conformity is inferred"
