"""Reuse contribution room while funding deposits from the dated IRA cash book.

Annual basis additions follow funded amounts, not requested orders. The
opening December balances remain the RMD base; later deposits cannot change
that prior-year value. Cash chronology and annual tax aggregation are distinct.
"""

from decimal import Decimal

from wealthlab.retirement.contribution_capacity import allowed
from wealthlab.retirement.contributions import KINDS, summary

ZERO = Decimal(0)


def initialize(case, book):
    book["contribution_rows"] = []
    people = [] if case.contributions is None else case.contributions.contributors
    book["contribution_used"] = {p.id: dict.fromkeys(KINDS, ZERO) for p in people}


def fund(case, book, order):
    plan = case.contributions
    person = next(p for p in plan.contributors if p.id == order.owner)
    used = book["contribution_used"][person.id]
    cap = allowed(plan, person, order, used)
    paid = min(cap, book["cash"])
    book["cash"] -= paid
    book["balances"][order.destination] += paid
    used[order.kind] += paid
    book["contribution_rows"].append(
        dict(
            id=order.id,
            date=order.date,
            owner=order.owner,
            destination=order.destination,
            kind=order.kind,
            requested=order.amount,
            eligible=cap,
            funded=paid,
            blocked_by_limit=order.amount - cap,
            unfunded=cap - paid,
        )
    )


def summaries(case, book):
    if case.contributions is None:
        return []
    return [
        summary(case.contributions, p, book["contribution_used"][p.id])
        for p in case.contributions.contributors
    ]


def owners(case, additions):
    by_owner = {r["owner"]: r for r in additions}
    return [add_basis(p, by_owner[p.id], case.year) if p.id in by_owner else p for p in case.owners]


def add_basis(person, added, year):
    roth = added["roth_ira"]
    return person.model_copy(
        update=dict(
            federal_ira_basis=person.federal_ira_basis + added["new_federal_ira_basis"],
            nj_ira_basis=person.nj_ira_basis + added["new_nj_ira_basis"],
            roth_regular_basis=person.roth_regular_basis + roth,
            nj_roth_basis=person.nj_roth_basis + roth,
            roth_first_year=person.roth_first_year
            if person.roth_first_year is not None or not roth
            else year,
        )
    )
