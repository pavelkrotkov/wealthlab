"""Recognize distributions separately from receipts and preserve the filing unit's other income.

Entitlements can be receivable after the tax-recognition date, or paid before a
projection has observed enough holding days for qualified treatment. Only taxable
accounts feed annual income. Retirement receipts stay inside their own wrapper."""

from collections import defaultdict
from decimal import Decimal

from wealthlab.portfolio.dividend_holding import amounts
from wealthlab.tax.annual import AnnualCase


def income(case, book, year, as_of):
    events = {item.id: item for item in case.distributions}
    federal, nj = defaultdict(Decimal), defaultdict(Decimal)
    pending = Decimal(0)
    for row in book.distributions:
        event = events[row["distribution"]]
        if not reportable(book, row, event, year):
            continue
        qualified, unresolved = amounts(book, event, row, as_of)
        federal[event.federal_character] += row["amount"]
        federal["qualified_dividends"] += qualified
        pending += unresolved
        if event.nj_character != "exempt":
            nj[event.nj_character] += row["amount"]
    return dict(federal), dict(nj), pending


def reportable(book, row, event, year):
    return (
        row["recognized"]
        and event.recognition_date.year == year
        and book.accounts[row["account_id"]].wrapper == "taxable"
    )


def include(case, federal, nj):
    payload = case.model_dump()
    for field, amount in federal.items():
        payload["federal_income"][field] += amount
    for field, amount in nj.items():
        payload["nj_income"][field] += amount
    return AnnualCase.model_validate(payload)


def details(case, book, as_of):
    events = {item.id: item for item in case.distributions}
    rows = []
    for row in book.distributions:
        event = events[row["distribution"]]
        qualified, pending = amounts(book, event, row, as_of)
        rows.append(
            dict(
                row,
                taxable_account=book.accounts[row["account_id"]].wrapper == "taxable",
                acquired=row["acquired"].isoformat(),
                ex_date=event.ex_date.isoformat(),
                payment_date=event.payment_date.isoformat(),
                recognition_date=event.recognition_date.isoformat(),
                qualified=qualified,
                qualification_pending=pending,
                federal_character=event.federal_character,
                nj_character=event.nj_character,
            )
        )
    return rows
