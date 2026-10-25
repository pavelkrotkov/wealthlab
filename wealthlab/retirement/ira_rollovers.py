"""Incoming eligible plan cash increases an IRA once without creating spendable cash.

The source plan is outside this annual IRA book. A household adapter must debit
its actual source before providing this funded receipt. Receipt-date balances
and annual owner-wide basis reconciliation deliberately have different timing.
"""

from decimal import Decimal

ZERO = Decimal(0)


def validate(case, accounts):
    for item in case.incoming_rollovers:
        target = accounts.get(item.destination)
        if target is None or target.product != "traditional_ira":
            raise ValueError("Incoming plan cash requires an ordinary traditional IRA destination.")
        if target.owner != item.owner or item.source in accounts:
            raise ValueError(
                "Direct incoming rollover keeps its owner and has a source outside the IRA book."
            )


def receive(book, item):
    book["balances"][item.destination] += item.amount
    book["rollover_rows"].append(
        dict(
            id=item.id,
            date=item.date,
            owner=item.owner,
            source=item.source,
            destination=item.destination,
            amount=item.amount,
            federal_basis_transferred=item.federal_basis_transferred,
            nj_basis_transferred=item.nj_basis_transferred,
            profile=item.profile,
        )
    )


def owners(people, rows):
    result = []
    for person in people:
        actual = [r for r in rows if r["owner"] == person.id]
        federal = sum((r["federal_basis_transferred"] for r in actual), ZERO)
        nj = sum((r["nj_basis_transferred"] for r in actual), ZERO)
        result.append(
            person.model_copy(
                update=dict(
                    federal_ira_basis=person.federal_ira_basis + federal,
                    nj_ira_basis=person.nj_ira_basis + nj,
                )
            )
        )
    return result
