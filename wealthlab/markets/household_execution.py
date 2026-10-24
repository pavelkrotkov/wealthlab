"""One realized path supplies marks, yield cash, locks and spending inflation.

Opening holdings earn the supplied month's cash yield on opening marked value.
The explicitly assumed ordinary tax character enters the same annual return;
actual cash arrives once before month-end sales. This is a monthly scenario
convention, not an issuer ex-date calendar or qualified-dividend determination.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.markets.guardrails import Guardrail
from wealthlab.tax.projection_inputs import TaxEvent


class Execution:
    def __init__(self, scenario, batch, binding, index):
        self.scenario, self.batch, self.binding, self.index = scenario, batch, binding, index
        self.guardrail = (
            Guardrail(scenario, binding.spending_guardrail) if binding.spending_guardrail else None
        )
        self.month = 0
        self.cpi = Decimal(1)
        self.factors = {b.security_id: batch.assets.index(b.factor) for b in binding.securities}

    def start(self, scenario, lots, start):
        month = self.month
        lots.locked = {
            security
            for security, factor in self.factors.items()
            if self.batch.locked[month, factor]
        }
        event = self.yield_event(lots, start)
        self.cash_yield = event.cash_received
        indexed = set(self.binding.inflation_expenses)
        expenses = [
            e.model_copy(update=dict(monthly_amount=money(e.monthly_amount * self.cpi)))
            if e.id in indexed
            else e
            for e in scenario.expenses
        ]
        self.cpi *= Decimal(str(1 + self.batch.inflation[self.index, month]))
        self.month += 1
        live = scenario.model_copy(update=dict(expenses=expenses))
        if self.guardrail:
            live = self.guardrail.apply(live, start)
        return live, (event,)

    def yield_event(self, lots, start):
        fed, nj, cash = {}, {}, Decimal(0)
        for binding in self.binding.securities:
            rate = Decimal(
                str(
                    self.batch.cash_yields[
                        self.index, self.month, self.factors[binding.security_id]
                    ]
                )
            )
            quantity = sum(
                (
                    lot.quantity
                    for lot in lots.book.lots.values()
                    if lot.security_id == binding.security_id
                ),
                Decimal(0),
            )
            amount = money(quantity * lots.prices[binding.security_id] * rate)
            cash += amount
            fed[binding.federal_cash_character] = (
                fed.get(binding.federal_cash_character, 0) + amount
            )
            if binding.nj_cash_character != "exempt":
                key = binding.nj_cash_character
                nj[key] = nj.get(key, 0) + amount
        return TaxEvent(
            date=start,
            description="Realized opening-holdings market cash yield",
            cash_received=cash,
            federal=fed,
            new_jersey=nj,
        )

    def observe(self, lots, row):
        values = {
            s: sum(
                (
                    lot.quantity * lots.prices[s]
                    for lot in lots.book.lots.values()
                    if lot.security_id == s
                ),
                Decimal(0),
            )
            for s in self.factors
        }
        assets = sum(row["account_balances"].values(), Decimal(0))
        row.update(
            market_cpi=self.cpi,
            market_cash_yield=self.cash_yield,
            market_locked_securities=sorted(lots.locked),
            market_security_values=values,
            market_max_security_weight=max(values.values(), default=Decimal(0)) / assets
            if assets
            else Decimal(0),
        )
        row["real_net_wealth"] = money(row["net_wealth"] / self.cpi)

        if self.guardrail:
            self.guardrail.observe(row)

    def finish(self, rows):
        rows[-1]["real_net_wealth"] = money(rows[-1]["net_wealth"] / self.cpi)
