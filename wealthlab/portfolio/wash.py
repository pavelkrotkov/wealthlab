"""Federal stock wash tracking; unresolved windows remain explicitly provisional."""

from decimal import Decimal

from wealthlab.portfolio.wash_match import match
from wealthlab.portfolio.wash_results import finish_row


class WashLedger:
    def __init__(self, case):
        self.enabled = case.federal_wash_tracking
        self.used = set()
        self.losses = []

    def after_trade(self, book, first_disposal):
        if not self.enabled:
            return
        for row in book.disposals[first_disposal:]:
            initialize(row, book)
            if row["wash_unmatched_quantity"]:
                self.losses.append(row)
        for row in self.losses:
            match(book, row, self.used)

    def finish(self, book, end):
        if not self.enabled:
            return
        for row in book.disposals:
            finish_row(row, book, end)


def initialize(row, book):
    taxable = book.accounts[row["account_id"]].wrapper == "taxable"
    security = book.securities[row["security_id"]]
    loss = taxable and row["federal_gross_gain"] < 0 and security.kind != "collectible"
    row.update(
        federal_wash_disallowed=Decimal(0),
        federal_wash_deferred=Decimal(0),
        federal_wash_permanent=Decimal(0),
        wash_matches=[],
        wash_unmatched_quantity=row["quantity"] if loss else Decimal(0),
    )
