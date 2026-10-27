"""Recognize reference gains in the sale year while explicitly closing complete wash windows."""

from datetime import timedelta
from decimal import Decimal

from wealthlab.portfolio.nj_recognition import finish as finish_nj
from wealthlab.portfolio.tax_recognition import gains
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent

ZERO = Decimal(0)


def recognition_date(ledger, observation):
    future_buys = any(
        (o.capital_call or ledger.call_owed)
        and observation.date < o.date <= (observation.date + timedelta(days=30))
        for o in ledger.plan.observations
    )
    if not future_buys:
        # Explicit no-external-identical-trades confirmation covers the forward window.
        return observation.date + timedelta(days=30)
    return observation.date


def recognize(ledger, when, recognition_end):
    book = ledger.reference_book
    book.wash.finish(book, recognition_end)
    finish_nj(ledger.reference_case, book, recognition_end)
    federal, nj, pending = gains(book, when.year)
    if when.month == 12 and any(pending.values()):
        raise ValueError(
            "Reference year-end pending wash losses need a January reconciliation adapter."
        )
    previous = ledger.reference_reported.get(when.year, (dict.fromkeys(federal, ZERO), ZERO))
    delta = {key: value - previous[0][key] for key, value in federal.items()}
    ledger.reference_reported[when.year] = (federal, nj)
    return TaxEvent(
        date=when,
        description="Actual liquid reference share gains",
        cash_received=0,
        federal=FederalIncome(**delta),
        new_jersey=NJIncome(dispositions=nj - previous[1]),
    )
