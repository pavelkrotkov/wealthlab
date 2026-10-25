"""Prior-December plan requirements share actual cash withdrawals within each plan.

Later deposits and market marks never change the current year's denominator.
An excess withdrawal cannot satisfy another plan or the following year's RMD.
"""

from decimal import ROUND_CEILING, Decimal

from wealthlab.retirement.rmd import divisor
from wealthlab.retirement.workplace_rmd_eligibility import owner_context

ZERO = Decimal(0)


class Ledger:
    def __init__(self, scenario):
        cash = scenario.workplace_plan.cash_withdrawals
        self.config = cash.rmd
        accounts = {a.id: a for a in scenario.accounts}
        members = {m.id: m for m in scenario.members}
        self.people = {
            gid: owner_context(group, cash, accounts, members)
            for gid, group in self.config.groups.items()
        }
        self.source_group = {
            s: gid for gid, group in self.config.groups.items() for s in group.sources
        }
        self.current: dict[str, dict] = {}
        self.audit: list[dict] = []
        self.year = None

    def start(self, wallet, when):
        if self.year == when.year:
            return
        self.year = when.year
        self.current = {}
        for gid, group in self.config.groups.items():
            balances = {s: wallet.balances[s] for s in group.sources}
            factor = divisor(self.people[gid], when.year)
            required = ZERO
            if factor is not None:
                required = (sum(balances.values(), ZERO) / factor).quantize(
                    Decimal(".01"), rounding=ROUND_CEILING
                )
            row = dict(
                year=when.year,
                plan=gid,
                sources=list(group.sources),
                prior_december_balances=balances,
                divisor=factor,
                required=required,
                withdrawn=ZERO,
                shortfall=None,
                excise_tax=ZERO,
                status="in_year",
                excise_treatment=self.config.shortfall_treatment,
                rmd_table=group.rmd_table,
                rule_mode=self.config.rule_mode,
            )
            self.current[gid] = row
            self.audit.append(row)

    def remaining(self, gid):
        row = self.current[gid]
        return max(ZERO, row["required"] - row["withdrawn"])

    def consume(self, source, gross):
        gid = self.source_group[source]
        required_part = min(gross, self.remaining(gid))
        self.current[gid]["withdrawn"] += gross
        return required_part


def make(scenario):
    cash = scenario.workplace_plan.cash_withdrawals
    return Ledger(scenario) if cash is not None and cash.rmd is not None else None


def start(book, wallet, when):
    if book is not None:
        book.start(wallet, when)


def consume(book, source, gross):
    return book.consume(source, gross) if book is not None else ZERO
