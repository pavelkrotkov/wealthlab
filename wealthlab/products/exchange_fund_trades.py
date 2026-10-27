"""Actual basket share disposals use existing selection and gain-character mechanisms."""

from datetime import timedelta

from wealthlab.household.calendar import money
from wealthlab.portfolio.nj_recognition import finish as finish_nj
from wealthlab.portfolio.orders import Trade
from wealthlab.products.exchange_fund_lots import ZERO
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


def order(lot, when, prices, identity):
    return Trade(
        id=f"{identity}_{lot.id}",
        provenance="assumption",
        date=when,
        action="sell",
        account_id=lot.account_id,
        security_id=lot.security_id,
        quantity=lot.quantity,
        price=prices[lot.security_id],
        commission=0,
        selection="specific",
        lot_ids=[lot.id],
    )


def sell(book, plan, prices, when, identity):
    first = len(book.disposals)
    for lot in list(book.lots.values()):
        if lot.security_id != plan.source_security.id:
            book.trade(order(lot, when, prices, identity))
    return recognized(book, plan, first, when, "Actual diversified basket sale; no duplicate cash")


def recognized(book, plan, first, when, description):
    # Supplied no-external-identical-trades scope closes only the known forward window.
    book.wash.finish(book, when + timedelta(days=30))
    finish_nj(plan, book, when + timedelta(days=30))
    rows = book.disposals[first:]
    federal = dict(short_term=ZERO, long_term=ZERO)
    nj = ZERO
    for row in rows:
        federal[row["federal_character"]] += row["federal_recognized_gain"]
        nj += row["nj_recognized_gain"]
    return TaxEvent(
        date=when,
        description=description,
        cash_received=0,
        federal=FederalIncome(**federal),
        new_jersey=NJIncome(dispositions=nj),
    )


def marked(book, prices):
    return sum((money(lot.quantity * prices[lot.security_id]) for lot in book.lots.values()), ZERO)


def direct_contribution(book, plan, when):
    """Sell actual selected source shares before reinvesting; retained wash basis stays in place."""
    from wealthlab.products.exchange_fund_lots import event

    trade = order(plan.source_lot, when, plan.opening_prices, "direct_contribution")
    trade = trade.model_copy(update={"quantity": plan.contribution_quantity})
    book.trade(trade)
    book.wash.finish(book, when + timedelta(days=30))
    finish_nj(plan, book, when + timedelta(days=30))
    row = book.disposals[-1]
    value = book.cash[plan.account_id]
    book.cash[plan.account_id] = ZERO
    return (
        value,
        dict(federal=value, nj=value),
        event(
            when,
            row["federal_recognized_gain"],
            row["nj_recognized_gain"],
            row["federal_character"],
        ),
    )
