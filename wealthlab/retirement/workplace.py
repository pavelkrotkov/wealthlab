"""Fund dated employee elections from gross wages before taxes and spending.

Annual limits share actual funded pretax and Roth amounts per owner. A dated
request consumes the current month's gross wage room, not later salary or
another spouse's earnings. The monthly budget pools receipts; it does not
certify intramonth payroll liquidity. Ties retain supplied election order.

Only funded contributions reduce cash and increase a retirement account.
Limit-blocked, current-wage-blocked and cash-unfunded amounts remain separate
in the audit. Optional unfilled elections are not themselves spending
failures; any resulting inability to meet taxes or spending remains visible.

Prior-year employer wages and plan permissions are explicit annual forecasts.
There is one sponsoring employer per owner; no match, vesting, rollover,
withdrawal or later excess correction is invented.
"""

from decimal import Decimal

from wealthlab.retirement.contribution_rules import workplace_limits
from wealthlab.retirement.workplace_returns import apply as apply_returns
from wealthlab.retirement.workplace_tax import events, summarize, tax_amounts
from wealthlab.retirement.workplace_validation import validate
from wealthlab.retirement.workplace_wages import gross_wages

ZERO = Decimal(0)


class Ledger:
    def __init__(self, scenario):
        validate(scenario)
        self.plan = scenario.workplace_plan
        self.members = [m.id for m in scenario.members]
        self.rules = scenario.tax_plan.income_rules
        self.used = {}
        self.log = []
        self.market_log = []

    def month(self, wallet, amounts, start, end):
        context = next(y for y in self.plan.years if y.year == start.year)
        people = {p.id: p for p in context.contributors}
        remaining = gross_wages(amounts, self.rules, self.members)
        excluded = dict.fromkeys(self.members, ZERO)
        rows = []
        for order in sorted(self.plan.orders, key=lambda o: o.date):
            if start <= order.date < end:
                row = self.fund(context, people[order.owner], order, wallet, remaining)
                rows.append(row)
                if order.kind == "pretax_401k":
                    excluded[order.owner] += row["funded"]
        self.remaining_wages = remaining
        self.log.extend(rows)
        summary = summarize(rows)
        summary["workplace_market_change"] = apply_returns(
            self.plan, wallet, start, end, self.market_log
        )
        return (
            tax_amounts(amounts, self.rules, self.members, excluded),
            events(self.members, excluded, start),
            summary,
        )

    def fund(self, context, person, order, wallet, remaining):
        used = self.used.setdefault((context.year, person.id), dict(total=ZERO, pretax=ZERO))
        total, pretax = workplace_limits(person, context)
        cap = max(ZERO, min(order.amount, total - used["total"]))
        if order.kind == "pretax_401k":
            cap = max(ZERO, min(cap, pretax - used["pretax"]))
        wage_cap = min(cap, remaining[order.owner])
        funded = wallet.pay(wage_cap)
        wallet.balances[order.destination] += funded
        used["total"] += funded
        remaining[order.owner] -= funded
        if order.kind == "pretax_401k":
            used["pretax"] += funded
        return dict(
            id=order.id,
            date=order.date.isoformat(),
            owner=order.owner,
            destination=order.destination,
            kind=order.kind,
            requested=order.amount,
            eligible=cap,
            funded=funded,
            blocked_by_limit=order.amount - cap,
            blocked_by_current_wages=cap - wage_cap,
            unfunded=wage_cap - funded,
        )


def make(scenario):
    return Ledger(scenario) if scenario.workplace_plan else None


def month(ledger, wallet, amounts, start, end):
    return ledger.month(wallet, amounts, start, end) if ledger else (amounts, (), {})
