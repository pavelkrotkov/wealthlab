"""Actual share trades and independent supplied basket bases use the ordinary lot book."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.book import Book
from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.disposal import dispose
from wealthlab.portfolio.lot_parts import split
from wealthlab.portfolio.models import TradingAccount
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent

ZERO = Decimal(0)


def opening(plan, scenario):
    case = LotCase(
        as_of=scenario.start,
        end=scenario.end,
        accounts=[
            TradingAccount(
                id=plan.account_id,
                provenance="assumption",
                owner="primary",
                wrapper="taxable",
                cash=0,
            )
        ],
        securities=[plan.source_security, *(b.security for b in plan.basket)],
        lots=[plan.source_lot],
        trades=[],
        closing_prices=plan.opening_prices,
        federal_wash_tracking=True,
        opening_wash_context_complete=True,
        nj_wash_treatment=plan.nj_wash_treatment,
    )
    return case, Book(case)


def take_source(book, plan):
    taken, remaining = split(book.lots[plan.source_lot.id], plan.contribution_quantity)
    del book.lots[plan.source_lot.id]
    if remaining.quantity:
        book.lots[remaining.id] = remaining
    return taken


def event(when, federal=ZERO, nj=ZERO, character="long_term"):
    return TaxEvent(
        date=when,
        description="Conditional exchange recognition; cash applied once",
        cash_received=0,
        federal=FederalIncome(**{character: federal}),
        new_jersey=NJIncome(dispositions=nj),
    )


def contribution(book, plan, when):
    if plan.mode == "direct_sale":
        from wealthlab.products.exchange_fund_trades import direct_contribution

        return direct_contribution(book, plan, when)
    taken = take_source(book, plan)
    value = money(taken.quantity * plan.opening_prices[taken.security_id])
    from wealthlab.products.exchange_fund_trades import order

    trade = order(taken, when, plan.opening_prices, "contribution")
    _, row = dispose(taken, taken.quantity, value, trade)
    federal = row["federal_gross_gain"] if plan.federal_contribution == "denied" else ZERO
    nj = row["nj_gross_gain"] if plan.nj_contribution == "denied" else ZERO
    if min(federal, nj) < 0:
        raise ValueError("Taxable loss contributions require a separate legal/wash adapter.")
    bases = dict(federal=taken.federal_basis + federal, nj=taken.nj_basis + nj)
    return value, bases, event(when, federal, nj, row["federal_character"])
