"""Audit supplied executed events without turning tax savings into spending cash."""

from decimal import Decimal

from wealthlab.products.life_contract_annual import compare
from wealthlab.products.life_contract_book import PolicyBook
from wealthlab.products.life_contract_values import values

ZERO = Decimal(0)


def run(case):
    contract = case.contract
    book = PolicyBook(contract.opening_federal_basis, contract.opening_loan)
    rows = [book.apply(contract, event) for event in contract.events]
    return dict(
        synthetic=case.synthetic,
        inputs=case.model_dump(mode="json"),
        rows=rows,
        values=values(case, rows),
        annual=compare(case, rows),
        external_cash=sum((r["external_cash"] for r in rows), ZERO),
        closing_loan=book.loan,
        closing_federal_basis=book.basis,
        closed=book.closed,
        closed_contract_asset=ZERO if book.closed else None,
        **premium_summary(case),
    )


def premium_summary(case):
    premiums = [e for e in case.contract.events if e.kind == "premium"]
    retired = case.retirement_date
    later = None
    if retired is not None:
        later = sum((e.amount for e in premiums if e.date >= retired), ZERO)
    return dict(
        premium_paid=sum((e.amount for e in premiums), ZERO), premiums_from_retirement=later
    )
