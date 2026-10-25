"""Expose unmet RMDs independently of spending and assess explicit conditional excise tax.

December is the elected deadline even for a first RMD year. The ordinary
25% case is the default. Reduced/canceled excise is a supplied contingent tax
outcome, not a claim that correction or IRS waiver eligibility was established.
"""

from datetime import date
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent

ZERO = Decimal(0)
RATES = {
    "ordinary_25_percent": Decimal(".25"),
    "timely_correction_10_percent_assumption": Decimal(".10"),
    "irs_waiver_allowed_assumption": ZERO,
}


def month(book, start, end):
    if book is None:
        return [], {}
    shortfall, excise = finalize(book) if end.year > start.year else (ZERO, ZERO)
    events = [tax_event(start.year, excise)] if excise else []
    return events, dict(
        summary(book, start.year),
        workplace_rmd_shortfall=shortfall,
        workplace_rmd_excise_tax=excise,
    )


def finalize(book):
    shortfall, excise = ZERO, ZERO
    for gid, row in book.current.items():
        row["shortfall"] = book.remaining(gid)
        shortfall += row["shortfall"]
        total = money(shortfall * RATES[book.config.shortfall_treatment])
        row["excise_tax"] = total - excise
        row["status"] = "closed"
        excise = total
    return shortfall, excise


def summary(book, year):
    return dict(
        workplace_rmd_required=sum((r["required"] for r in book.current.values()), ZERO),
        workplace_rmd_distributed=sum((r["withdrawn"] for r in book.current.values()), ZERO),
        workplace_rmd_remaining=sum((book.remaining(gid) for gid in book.current), ZERO),
        workplace_rmd_unresolved_prior=pending(book, year),
    )


def pending(book, year):
    return sum((r["shortfall"] or ZERO for r in book.audit if r["year"] < year), ZERO)


def tax_event(year, amount):
    return TaxEvent(
        date=date(year, 12, 31),
        description="Conditional workplace RMD shortfall excise",
        cash_received=ZERO,
        federal=FederalIncome(retirement_additional_tax=amount),
        new_jersey=NJIncome(),
    )
