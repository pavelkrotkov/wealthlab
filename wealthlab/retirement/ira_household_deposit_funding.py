"""Actual wallet cash funds optional IRA requests before current tax and spending.

Requests settle at month end after all IRA returns/withdrawals in that month.
The combined annual engine receives only those funded deposits, each with an
equal internal funding receipt. Its own withdrawal cash is never deposited in
the household a second time. Failed optional requests are not retried.
"""

from calendar import monthrange
from datetime import date
from decimal import Decimal

from wealthlab.retirement.contribution_capacity import allowed
from wealthlab.retirement.contributions import KINDS
from wealthlab.retirement.ira_household_deposit_validation import PREFIX

ZERO = Decimal(0)


class Funding:
    def __init__(self, plan):
        self.plan = plan
        self.used = {}
        self.orders = []
        self.receipts = []
        self.audit = []

    def month(self, context, wallet, start, end):
        if self.plan is None:
            return {}
        people = {p.id: p for p in context.contributors}
        rows = []
        for order in sorted(self.plan.orders, key=lambda o: o.date):
            if start <= order.date < end:
                rows.append(self.fund(context, people[order.owner], order, wallet, start))
        return dict(
            ira_contributions=sum((r["funded"] for r in rows), ZERO),
            ira_contributions_unfilled=sum((r["requested"] - r["funded"] for r in rows), ZERO),
        )

    def fund(self, context, person, order, wallet, start):
        used = self.used.setdefault((context.year, person.id), dict.fromkeys(KINDS, ZERO))
        cap = allowed(context, person, order, used)
        funded = wallet.pay(cap)
        used[order.kind] += funded
        effective = date(start.year, start.month, monthrange(start.year, start.month)[1])
        if funded:
            self.orders.append(order.model_copy(update=dict(date=effective, amount=funded)))
            self.receipts.append(
                dict(
                    id=f"{PREFIX}{len(self.orders)}",
                    provenance="assumption",
                    date=effective,
                    amount=funded,
                )
            )
        row = dict(
            id=order.id,
            date=order.date.isoformat(),
            settlement_date=effective.isoformat(),
            owner=order.owner,
            destination=order.destination,
            kind=order.kind,
            requested=order.amount,
            eligible=cap,
            funded=funded,
            blocked_by_limit=order.amount - cap,
            unfunded=cap - funded,
        )
        self.audit.append(row)
        return row
