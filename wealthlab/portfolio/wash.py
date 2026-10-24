"""Jurisdiction-specific stock wash tracking; unresolved windows remain explicitly provisional."""

from decimal import Decimal

from wealthlab.portfolio.wash_keys import key
from wealthlab.portfolio.wash_match import match
from wealthlab.portfolio.wash_results import finish_row


class WashLedger:
    def __init__(self, case, jurisdiction="federal"):
        self.jurisdiction = jurisdiction
        self.enabled = (
            case.federal_wash_tracking
            if jurisdiction == "federal"
            else case.nj_wash_treatment == "federal_rules"
        )
        self.used = set()
        self.losses = []

    def after_trade(self, book, first_disposal):
        if not self.enabled:
            return
        for row in book.disposals[first_disposal:]:
            initialize(row, book, self.jurisdiction)
            if row[key(self.jurisdiction, "unmatched_quantity")]:
                self.losses.append(row)
        for row in self.losses:
            match(book, row, self.used, self.jurisdiction)

    def finish(self, book, end):
        if not self.enabled:
            return
        for row in book.disposals:
            finish_row(row, book, end, self.jurisdiction)


def initialize(row, book, jurisdiction):
    taxable = book.accounts[row["account_id"]].wrapper == "taxable"
    security = book.securities[row["security_id"]]
    loss = taxable and row[jurisdiction + "_gross_gain"] < 0 and security.kind != "collectible"
    for field in ("disallowed", "deferred", "permanent"):
        row[key(jurisdiction, field)] = Decimal(0)
    row[key(jurisdiction, "matches")] = []
    row[key(jurisdiction, "unmatched_quantity")] = row["quantity"] if loss else Decimal(0)
