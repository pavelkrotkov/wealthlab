"""A trade is validated before any cash or lot mutation; cash never finances itself."""

from decimal import Decimal
from itertools import chain

from wealthlab.household.calendar import money
from wealthlab.portfolio.disposal import dispose, split_proceeds
from wealthlab.portfolio.fees import settle
from wealthlab.portfolio.purchase import buy
from wealthlab.portfolio.selection import select
from wealthlab.portfolio.wash import WashLedger


class Book:
    def __init__(self, case):
        self.accounts = {item.id: item for item in case.accounts}
        self.securities = {item.id: item for item in case.securities}
        self.lots = {item.id: item for item in case.lots}
        self.allocated_ids = {
            item.id
            for item in chain(
                case.lots,
                case.trades,
                case.sale_policies,
                case.harvest_policies,
                case.fee_schedules,
            )
        }
        # Splitting a replacement must preserve purchase order independently of lot IDs.
        self.share_order = {lot.id: (index, Decimal(0)) for index, lot in enumerate(case.lots)}
        self.origins = {item.id: item.id for item in case.lots}
        self.cash = {item.id: item.cash for item in case.accounts}
        self.fee_owed = dict.fromkeys(self.accounts, Decimal(0))
        self.fee_paid = dict.fromkeys(self.accounts, Decimal(0))
        self.fee_assessments = []
        self.disposals = []
        self.history = []
        self.harvest_sales = set()
        self.harvest_decisions = []
        self.wash = WashLedger(case)
        self.nj_wash = WashLedger(case, "nj")

    def trade(self, trade):
        """Both tax ledgers observe the same executed shares and cash movements."""
        first = len(self.disposals)
        if trade.action == "buy":
            buy(self, trade)
        else:
            self.sell(trade)
        settle(self, trade.account_id)
        self.history.append(trade)
        self.wash.after_trade(self, first)
        self.nj_wash.after_trade(self, first)

    def sell(self, trade):
        portions = select(self.lots, trade)
        proceeds = money(trade.quantity * trade.price) - trade.commission
        if proceeds < 0:
            raise ValueError("Sale commission exceeds gross proceeds.")
        updates = [
            dispose(lot, qty, value, trade)
            for lot, qty, value in split_proceeds(portions, trade, proceeds)
        ]
        for remaining, row in updates:
            if remaining.quantity:
                self.lots[remaining.id] = remaining
            else:
                del self.lots[remaining.id]
            self.disposals.append(row)
        self.cash[trade.account_id] += proceeds
