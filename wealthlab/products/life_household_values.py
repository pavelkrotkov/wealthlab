"""Net surrender value is the living household asset; death protection is separate."""

from datetime import timedelta
from decimal import Decimal

from wealthlab.products.life_illustration import loan_review

ZERO = Decimal(0)


def mark(ledger, holding, wallet, end):
    book = ledger.books[holding.account_id]
    if book.closed:
        gross = dict(cash=ZERO, surrender=ZERO, death=ZERO)
    else:
        value = next(v for v in holding.contract.values if v.date == end - timedelta(days=1))
        if loan_review(value.gross_cash_value, book.loan):
            raise ValueError(
                "In-force household policy needs confirmed loan-collateral continuation."
            )
        gross = dict(
            cash=value.gross_cash_value,
            surrender=value.gross_surrender_value,
            death=value.gross_death_benefit,
        )
    net = {name: max(ZERO, amount - book.loan) for name, amount in gross.items()}
    wallet.balances[holding.account_id] = net["surrender"]
    return dict(
        account_id=holding.account_id,
        owner=ledger.owners[holding.account_id],
        closed=book.closed,
        loan=book.loan,
        federal_basis=book.basis,
        net_cash_value=net["cash"],
        net_surrender_value=net["surrender"],
        net_death_benefit=net["death"],
    )
