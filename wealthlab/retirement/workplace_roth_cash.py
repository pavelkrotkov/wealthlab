"""Fund separated Roth plan cash and send only actual net receipts to the shared tax ledger."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.retirement.account_liquidity import blocked
from wealthlab.retirement.roth_reconciliation import half_birthday
from wealthlab.retirement.workplace_roth_tax import tax_event, withholding

ZERO = Decimal(0)


def month(ledger, wallet, start, end):
    if ledger.roth is None:
        return [], {}
    rows, events = [], []
    for order in sorted(ledger.roth.config.orders, key=lambda o: o.date):
        if start <= order.date < end:
            row, event = withdraw(ledger, wallet, order)
            rows.append(row)
            events.append(event)
    ledger.roth.audit.extend(rows)
    return events, dict(
        workplace_roth_withdrawal_gross=sum((r["gross"] for r in rows), ZERO),
        workplace_roth_withdrawal_net=sum((r["net_cash"] for r in rows), ZERO),
        workplace_roth_withdrawal_unfilled=sum((r["unfilled"] for r in rows), ZERO),
        workplace_roth_additional_tax=sum((r["additional_tax"] for r in rows), ZERO),
    )


def withdraw(ledger, wallet, order):
    locked = blocked(ledger.plan.liquidity_locks, order.source, order.date)
    gross = ZERO if locked else min(order.amount, wallet.balances[order.source])
    born = ledger.birth_dates[ledger.accounts[order.source].owner]
    book = ledger.roth
    recognized = book.distribute(order.source, gross, wallet, order.date, born)
    contract = book.config.contracts[recognized["contract"]]
    exception = contract.separation_date.year - born.year >= 55
    early = order.date < half_birthday(born)
    additional = (
        money(recognized["federal_taxable"] * Decimal(".10")) if early and not exception else ZERO
    )
    source = withholding(order, gross, recognized)
    wallet.balances[order.source] -= gross
    row = dict(
        id=order.id,
        date=order.date.isoformat(),
        source=order.source,
        requested=order.amount,
        gross=gross,
        net_cash=gross - source.total,
        unfilled=order.amount - gross,
        blocked_by_liquidity=locked,
        separation_age55_exception=exception,
        below_age59_half=early,
        additional_tax=additional,
        source_withholding=source.model_dump(),
        **recognized,
    )
    return row, tax_event(order, row, born)
