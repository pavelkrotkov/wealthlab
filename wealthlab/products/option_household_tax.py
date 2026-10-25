"""Actual realized share/option amounts enter the shared annual ledger without cash twice."""

from datetime import date
from decimal import Decimal

from wealthlab.products.option_household_dividends import events as dividend_events
from wealthlab.products.option_recognition import recognition
from wealthlab.products.option_tax_rows import stock_recognition
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


def events(state, start, end, seen):
    rows = recognition(state) + stock_recognition(state)
    result = []
    for row in rows:
        key = (row["id"], row["jurisdiction"])
        if key in seen or not start <= date.fromisoformat(row["date"]) < end:
            continue
        if row["recognized"] is None:
            raise ValueError("Unresolved option recognition cannot become zero household tax.")
        result.append(event(row))
        seen.add(key)
    return result + dividend_events(state, start, end, seen)


def event(row):
    federal, nj = FederalIncome(), NJIncome()
    if row["jurisdiction"] == "federal":
        federal = FederalIncome(short_term=row["short_term"], long_term=row["long_term"])
    else:
        nj = NJIncome(dispositions=row["recognized"])
    return TaxEvent(
        date=date.fromisoformat(row["date"]),
        description="Conditional option:" + row["id"],
        cash_received=Decimal(0),
        federal=federal,
        new_jersey=nj,
    )
