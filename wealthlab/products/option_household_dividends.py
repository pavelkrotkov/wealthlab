"""Confirmed ordinary dividends recognize actual cash receipts without a second deposit."""

from datetime import date

from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


def events(state, start, end, seen):
    result = []
    for index, row in enumerate(state.cash_movements):
        day = date.fromisoformat(row["date"])
        key = (f"dividend:{index}", "both")
        if row["label"] != "stock_dividend" or key in seen or not start <= day < end:
            continue
        result.append(
            TaxEvent(
                date=day,
                description=key[0],
                cash_received=0,
                federal=FederalIncome(dividends=row["amount"]),
                new_jersey=NJIncome(dividends=row["amount"]),
            )
        )
        seen.add(key)
    return result
