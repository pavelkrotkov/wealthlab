"""NJ recognition is explicit; an unconfirmed choice never becomes a zero tax benefit."""

from decimal import Decimal


def finish(case, book, as_of=None):
    if case.nj_wash_treatment == "federal_rules":
        book.nj_wash.finish(book, as_of or case.end)
        return
    for row in book.disposals:
        taxable = book.accounts[row["account_id"]].wrapper == "taxable"
        if case.nj_wash_treatment == "unconfirmed":
            row["nj_recognized_gain"] = None
            row["nj_status"] = "Unconfirmed NJ treatment; raw basis gain is not recognized income"
        else:
            row["nj_recognized_gain"] = row["nj_gross_gain"] if taxable else Decimal(0)
            row["nj_pending_loss"] = Decimal(0)
            row["nj_status"] = "Conditional no-wash assumption; separate NJ basis"
