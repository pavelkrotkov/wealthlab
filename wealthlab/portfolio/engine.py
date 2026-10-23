"""Gross lot accounting only; wash adjustments and household tax integration follow."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.book import Book
from wealthlab.portfolio.concentration import summarize
from wealthlab.portfolio.validation import validate


def run(case) -> dict:
    validate(case)
    book = Book(case)
    for trade in case.trades:
        book.trade(trade)
    values = {key: Decimal(0) for key in book.securities}
    for lot in book.lots.values():
        values[lot.security_id] += lot.quantity * case.closing_prices[lot.security_id]
    cash = sum(book.cash.values(), Decimal(0))
    wealth = cash + money(sum(values.values(), Decimal(0)))
    return dict(
        cash_by_account=book.cash,
        closing_cash=cash,
        security_values={key: money(value) for key, value in values.items()},
        gross_wealth=wealth,
        concentration=summarize(case, book, values, wealth),
        lots=[lot.model_dump(mode="json") for lot in book.lots.values()],
        disposals=book.disposals,
        transaction_costs=sum((trade.commission for trade in case.trades), Decimal(0)),
        scope="Gross lot accounting; no wash-sale adjustment, tax benefit or tax-funded sale yet.",
    )
