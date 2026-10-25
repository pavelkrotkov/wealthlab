"""Limited-liability investor cash wraps the existing internal long/short economic book."""

from datetime import timedelta

from wealthlab.products.long_short_book import ZERO, equity, opening, snapshot
from wealthlab.products.long_short_step import advance
from wealthlab.products.private_fund_dealing import deal, settle
from wealthlab.products.private_fund_tax import BasisBook


class FundLedger:
    def __init__(self, sleeve):
        self.sleeve = sleeve
        self.case = sleeve.case
        self.contract = sleeve.private_fund_contract
        self.book = opening(self.case)
        self.tax = BasisBook(self.contract, sleeve.account_id)
        self.settlements = []
        self.reserved = ZERO
        self.final_reserved = False

    def execute(self, month, wallet, start, end):
        when = end - timedelta(days=1)
        self.tax.adjust(start, end)
        observation = self.sleeve.observations[month].model_dump()
        row = advance(self.book, self.case, observation, when, month, False)
        # Internal forced sales leave cash in the fund; they are not investor distributions.
        if self.book["outside"] and not self.book["closed"]:
            raise ValueError("Unexpected private-fund external collateral movement.")
        row.update(self.reopen_cash())
        row.update(deal(self, when, observation["locked"]))
        cash, events = settle(self, wallet, when)
        row.update(snapshot(self.book))
        row.update(self.snapshot(cash))
        wallet.balances[self.sleeve.account_id] = row["equity"]
        row["terminal_exit_blocked"] = month == len(
            self.sleeve.observations
        ) - 1 and self.exit_blocked(when)
        return row, self.tax.release(events, start, end)

    def reopen_cash(self):
        cash = self.book["outside"]
        if cash:
            self.book.update(cash=cash, outside=ZERO)
        return dict(fund_internal_liquidation_cash=cash)

    def snapshot(self, cash):
        receivable = sum((s["cash"] for s in self.settlements), ZERO)
        raw = equity(self.book)
        return dict(
            account_id=self.sleeve.account_id,
            long_factor=self.case.long_factor,
            short_factor=self.case.short_factor,
            fund_internal_equity=raw,
            fund_nonrecourse_deficit=max(ZERO, -raw),
            fund_receivable=receivable,
            equity=max(ZERO, raw) + receivable,
            redemption_paid=cash,
            fund_basis=dict(self.tax.basis),
            fund_complete_liquidation=self.tax.closed,
            fund_tax_audit=list(self.tax.log),
            recourse_debt_paid=ZERO,
        )

    def exit_blocked(self, when):
        requested = any(
            r.complete_liquidation and r.notice_date <= when for r in self.contract.requests
        )
        return requested and not self.tax.closed
