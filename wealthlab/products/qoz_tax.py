"""QOZ stock tranches separate elected gain, ordinary stock basis and tax-only events."""

from datetime import date
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.long_short_book import ZERO
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


def event(when, description, federal=ZERO, nj=ZERO, character="long_term", dividend=ZERO):
    return TaxEvent(
        date=when,
        description=description,
        cash_received=ZERO,
        federal=FederalIncome(**{character: federal}, dividends=dividend),
        new_jersey=NJIncome(dispositions=nj, dividends=dividend),
    )


def opening(funded, elected, invested, character):
    return dict(
        funded=funded,
        invested=invested,
        character=character,
        jurisdictions={
            j: dict(elected=q, basis=ZERO, ordinary_basis=funded - q, included=False)
            for j, q in elected.items()
        },
        log=[],
    )


def inclusion_date(invested):
    return date(2026, 12, 31) if invested.year <= 2026 else invested.replace(year=invested.year + 5)


def include(tax, nav, when, plan, sale=False):
    """Apply the five-year basis increment before a tax-only original-character inclusion.

    A reduced inclusion due to FMV closes this deferral; a later recovery remains
    ordinary stock appreciation. The independently tracked stock basis carries
    the actual recognized gain into the eventual sale calculation.
    """
    values = dict(federal=ZERO, new_jersey=ZERO)
    due = inclusion_date(tax["invested"])
    for jurisdiction, book in tax["jurisdictions"].items():
        if not inclusion_due(book, sale, when, due):
            continue
        if when >= due and tax["invested"].year > 2026:
            step = money(
                book["elected"]
                * (Decimal("0.30") if plan.rural_30_percent_assumed_confirmed else Decimal("0.10"))
            )
            book["basis"] += step
        fmv = money(nav * book["elected"] / tax["funded"])
        amount = max(ZERO, min(book["elected"], fmv) - book["basis"])
        book["basis"] += amount
        book["included"] = True
        values[jurisdiction] = amount
        tax["log"].append(
            dict(
                date=when.isoformat(),
                jurisdiction=jurisdiction,
                event="deferred_gain_inclusion",
                amount=amount,
                fmv=fmv,
                statutory_due=due.isoformat(),
                basis=book["basis"],
            )
        )
    return event(
        when,
        "QOZ original-gain inclusion, no cash distribution",
        federal=values["federal"],
        nj=values["new_jersey"],
        character=tax["character"],
    )


def inclusion_due(book, sale, when, due):
    return not book["included"] and bool(book["elected"]) and (sale or when >= due)
