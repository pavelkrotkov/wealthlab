"""Reuse liquid lot selection and exact disposal; raise only cash actually available.

This does not model a recipient HSA distribution or its eligibility. It sells
permitted shares into the same HSA cash account, paying commission and prior
custodian-fee arrears first. A marked position is never itself spendable cash.
"""

from decimal import ROUND_UP, Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.fees import settle
from wealthlab.portfolio.generated_orders import identity
from wealthlab.portfolio.orders import Trade
from wealthlab.portfolio.selection import candidates

ZERO = Decimal(0)
UNIT = Decimal(".000001")


def fund(ledger, account, requested, when):
    settle(ledger.book, account)
    for n, source in enumerate(ledger.plan.funding_sources):
        if source.account_id == account and not ledger.locked(source.security_id, when):
            sell(ledger, source, n, requested, when)
    return min(requested, ledger.book.cash[account])


def sell(ledger, source, n, target, when):
    book = ledger.book
    needed = target - book.cash[source.account_id]
    if needed <= 0:
        return
    template = order(ledger, source, n, Decimal(1), when, reserve=False)
    available = sum((lot.quantity for lot in candidates(book.lots, template)), ZERO)
    if money(available * template.price) <= source.commission:
        return
    gross = needed + book.fee_owed[source.account_id] + source.commission
    quantity = min(available, (gross / template.price).quantize(UNIT, rounding=ROUND_UP))
    trade = order(ledger, source, n, quantity, when, reserve=True)
    book.trade(trade)
    ledger.generated.append(trade.model_dump(mode="json"))
    ledger.counter += 1


def order(ledger, source, n, quantity, when, *, reserve):
    prefix = f"hsa_raise_{when.isoformat().replace('-', '_')}_{n}"
    suffix = str(ledger.counter)
    key = identity(ledger.book, prefix, suffix) if reserve else prefix + "_" + suffix
    trade = Trade(
        id=key,
        provenance="assumption",
        date=when,
        action="sell",
        account_id=source.account_id,
        security_id=source.security_id,
        quantity=quantity,
        price=ledger.prices[source.security_id],
        commission=source.commission,
        selection="fifo" if source.selection == "nj_hifo" else source.selection,
    )
    if reserve and source.selection == "nj_hifo":
        lots = sorted(
            candidates(ledger.book.lots, trade),
            key=lambda lot: (-lot.nj_basis / lot.quantity, lot.acquired, lot.id),
        )
        data = trade.model_dump()
        data.update(selection="specific", lot_ids=[lot.id for lot in lots])
        return Trade.model_validate(data)
    return trade
