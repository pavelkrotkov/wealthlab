"""Report recognized versus pending federal losses without spending future tax benefits."""

from datetime import date, timedelta
from decimal import Decimal

from wealthlab.portfolio.wash_keys import key


def finish_row(row, book, end, jurisdiction):
    taxable = book.accounts[row["account_id"]].wrapper == "taxable"
    unresolved = row[key(jurisdiction, "unmatched_quantity")] and end < date.fromisoformat(
        row["date"]
    ) + timedelta(days=30)
    adjusted = row[jurisdiction + "_gross_gain"] + row[key(jurisdiction, "disallowed")]
    row[jurisdiction + "_recognized_gain"] = adjusted if taxable and not unresolved else Decimal(0)
    row[jurisdiction + "_pending_loss"] = -adjusted if taxable and unresolved else Decimal(0)
    row[jurisdiction + "_status"] = (
        "pending wash window" if unresolved else "modeled " + jurisdiction + " recognition"
    )
