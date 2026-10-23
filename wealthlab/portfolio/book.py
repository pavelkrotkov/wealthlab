"""A trade is validated before any cash or lot mutation; cash never finances itself."""

from wealthlab.household.calendar import money
from wealthlab.portfolio.disposal import dispose, split_proceeds
from wealthlab.portfolio.purchase import buy
from wealthlab.portfolio.selection import select
from wealthlab.portfolio.wash import WashLedger


class Book:
    def __init__(self, case):
        self.accounts = {item.id: item for item in case.accounts}
        self.securities = {item.id: item for item in case.securities}
        self.lots = {item.id: item for item in case.lots}
        self.origins = {item.id: item.id for item in case.lots}
        self.cash = {item.id: item.cash for item in case.accounts}
        self.disposals = []
        self.history = []
        self.wash = WashLedger(case)

    def trade(self, trade):
        first = len(self.disposals)
        if trade.action == "buy":
            buy(self, trade)
        else:
            self.sell(trade)
        self.history.append(trade)
        self.wash.after_trade(self, first)

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
