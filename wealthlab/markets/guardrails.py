"""Review only observed real wealth; spending reductions are explicit policy outcomes.

The reference is a high-water mark of actual real net wealth, including spending,
taxes and external receipts. It is not a return-only index. A binary cut has
hysteresis and never compounds itself or changes essential spending. Fresh
monthly inputs prevent a restored policy from retaining last month's reduction.
"""

from datetime import date
from decimal import Decimal

from wealthlab.household.calendar import amount, money

ZERO = Decimal(0)


class Guardrail:
    def __init__(self, scenario, plan):
        self.plan = plan
        self.peak = opening_wealth(scenario)
        self.latest = self.peak
        self.cut = False
        self.month = 0
        self.audit = {}

    def apply(self, scenario, start):
        reviewed = self.month > 0 and self.month % self.plan.review_interval_months == 0
        decline = max(ZERO, (self.peak - self.latest) / self.peak) if self.peak > 0 else ZERO
        if reviewed:
            self.review(decline)
        factor = 1 - self.plan.discretionary_cut_fraction if self.cut else Decimal(1)
        expenses = [
            e.model_copy(update=dict(monthly_amount=money(e.monthly_amount * factor)))
            if e.id in self.plan.expense_ids
            else e
            for e in scenario.expenses
        ]
        end = date(start.year + start.month // 12, start.month % 12 + 1, 1)
        reduction = sum(
            (
                amount(old, start, end, scenario) - amount(new, start, end, scenario)
                for old, new in zip(scenario.expenses, expenses, strict=True)
            ),
            ZERO,
        )
        self.audit = dict(
            guardrail_reviewed=reviewed,
            guardrail_cut_active=self.cut,
            guardrail_prior_real_drawdown=decline,
            guardrail_discretionary_reduction=reduction,
        )
        self.month += 1
        return scenario.model_copy(update=dict(expenses=expenses))

    def review(self, decline):
        if decline >= self.plan.trigger_real_wealth_drawdown:
            self.cut = True
        elif decline <= self.plan.restore_real_wealth_drawdown:
            self.cut = False

    def observe(self, row):
        row.update(self.audit)
        self.latest = row["real_net_wealth"]
        self.peak = max(self.peak, self.latest)


def validate(scenario, plan):
    if not plan.wealth_includes_spending_effects_confirmed:
        raise ValueError(
            "Confirm that guardrail real wealth includes spending and cash-flow effects."
        )
    if opening_wealth(scenario) <= 0:
        raise ValueError("Real-wealth drawdown guardrails require positive opening net wealth.")
    expenses = {e.id: e for e in scenario.expenses}
    if not set(plan.expense_ids) <= expenses.keys():
        raise ValueError("Unknown guardrail expense ID.")
    if any(expenses[i].category != "discretionary" for i in plan.expense_ids):
        raise ValueError("Guardrails can change only explicitly selected discretionary expenses.")


def opening_wealth(scenario):
    assets = sum(
        a.balance * Decimal(str(scenario.usd_per_currency[a.currency])) for a in scenario.accounts
    )
    debt = sum(
        d.balance * Decimal(str(scenario.usd_per_currency[d.currency])) for d in scenario.debts
    )
    return assets - debt
