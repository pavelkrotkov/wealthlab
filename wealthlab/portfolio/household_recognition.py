"""Recognize changes in actual wash-adjusted annual gains, never gross tax savings."""

from datetime import date
from decimal import Decimal

from wealthlab.portfolio.nj_recognition import finish as finish_nj
from wealthlab.portfolio.tax_recognition import gains, with_gains
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent

ZERO = Decimal(0)


def totals(case, book, when):
    book.wash.finish(book, when)
    finish_nj(case, book, when)
    return gains(book, when.year)


def delta(case, book, when, previous):
    federal, nj, pending = totals(case, book, when)
    before = previous.get(when.year, (dict.fromkeys(federal, ZERO), ZERO))
    change = {key: value - before[0][key] for key, value in federal.items()}
    return change, nj - before[1], (federal, nj), pending


def event(case, book, when, previous, allow_pending=False):
    federal, nj, current, pending = delta(case, book, when, previous)
    guard_year_end(when, pending, allow_pending)
    previous[when.year] = current
    return TaxEvent(
        date=when,
        description="Actual linked-lot recognized gains; no duplicated sale cash",
        cash_received=0,
        federal=FederalIncome(**federal),
        new_jersey=NJIncome(dispositions=nj),
    )


def apply(annual, case, book, when, previous, allow_pending=False):
    federal, nj, current, pending = delta(case, book, when, previous)
    guard_year_end(when, pending, allow_pending)
    return with_gains(annual, federal, nj), current


def guard_year_end(when, pending, allow_pending=False):
    if when == date(when.year, 12, 31) and any(pending.values()) and not allow_pending:
        raise ValueError("Year-end pending wash losses need January/prior-return reconciliation.")
