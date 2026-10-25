"""Debit actual vested plan assets and pass net cash plus source tax to the shared ledger.

The qualified-plan age-55 separation exception uses the calendar year of
separation, not the distribution year or household retirement-date setting.
It is distinct from IRA access. Withholding is a payment, never additional tax.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.retirement.account_liquidity import blocked
from wealthlab.retirement.roth_reconciliation import half_birthday
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.nj_retirement import RetirementEligibility
from wealthlab.tax.projection_inputs import TaxEvent
from wealthlab.tax.source_withholding import SourceWithholding

ZERO = Decimal(0)


def month(ledger, wallet, start, end):
    plan = ledger.plan.cash_withdrawals
    if plan is None:
        return [], {}
    rows, events = [], []
    for order in sorted(plan.orders, key=lambda o: o.date):
        if start <= order.date < end:
            row, event = withdraw(ledger, wallet, order, plan.profiles[order.source])
            rows.append(row)
            events.append(event)
    ledger.withdrawal_log.extend(rows)
    return events, dict(
        workplace_withdrawal_gross=sum((r["gross"] for r in rows), ZERO),
        workplace_withdrawal_net=sum((r["net_cash"] for r in rows), ZERO),
        workplace_withdrawal_unfilled=sum((r["unfilled"] for r in rows), ZERO),
        workplace_withdrawal_additional_tax=sum((r["additional_tax"] for r in rows), ZERO),
    )


def withdraw(ledger, wallet, order, profile):
    locked = blocked(ledger.plan.liquidity_locks, order.source, order.date)
    gross = ZERO if locked else min(order.amount, wallet.balances[order.source])
    wallet.balances[order.source] -= gross
    born = ledger.birth_dates[ledger.accounts[order.source].owner]
    separation_exception = profile.separation_date.year - born.year >= 55
    early = order.date < half_birthday(born)
    additional = money(gross * Decimal(".10")) if early and not separation_exception else ZERO
    source = SourceWithholding(
        gross_cash=gross,
        federal_income_withheld=money(gross * order.federal_withholding_rate),
        nj_withheld=money(gross * order.nj_withholding_rate),
    )
    # Independent cent rounding can overrun a one-cent distribution at rate ties.
    if source.total > gross:
        source = source.model_copy(update=dict(nj_withheld=gross - source.federal_income_withheld))
    net = gross - source.total
    event = TaxEvent(
        date=order.date,
        description=f"Workplace cash withdrawal: {order.id}",
        cash_received=net,
        withholding=source,
        federal=FederalIncome(taxable_pension=gross, retirement_additional_tax=additional),
        new_jersey=NJIncome(
            pension=gross,
            retirement=RetirementEligibility(
                qualified_pension=gross if order.date.year - born.year >= 62 else ZERO
            ),
        ),
    )
    return dict(
        id=order.id,
        date=order.date.isoformat(),
        source=order.source,
        requested=order.amount,
        gross=gross,
        net_cash=net,
        unfilled=order.amount - gross,
        source_withholding=source.model_dump(),
        additional_tax=additional,
        blocked_by_liquidity=locked,
        separation_age55_exception=separation_exception,
        below_age59_half=early,
    ), event
