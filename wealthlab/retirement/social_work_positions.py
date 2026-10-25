"""Separate government receivables, overpayment debt and cash, by recipient.

Only a paid benefit can produce a work overpayment. Future scheduled benefits
are never posted early. Supplied collection timing/fraction are conditional;
no waiver, interest, bankruptcy or special tax-credit election is inferred.
"""

from decimal import ROUND_HALF_UP, Decimal

ZERO = Decimal(0)
CENT = Decimal("0.01")


class Positions:
    def __init__(self, entries):
        self.entries = entries
        self.posted = set()
        self.positions = []

    def observe(self, when, inclusive):
        for number, entry in enumerate(self.entries):
            paid = entry["payment_month"] <= when if inclusive else entry["payment_month"] < when
            if number not in self.posted and entry["known_date"] <= when and paid:
                self.positions.append(dict(entry))
                self.posted.add(number)

    def settle(self, member, when, regular_cash, fraction):
        due = self.due(member, when)
        credit = sum((max(ZERO, p["amount"]) for p in due), ZERO)
        debt = -sum((min(ZERO, p["amount"]) for p in due), ZERO)
        offset = min(credit, debt)
        credit, debt = credit - offset, debt - offset
        recovery = min(debt, (regular_cash * fraction).quantize(CENT, rounding=ROUND_HALF_UP))
        debt -= recovery
        self.positions = [p for p in self.positions if p not in due]
        if debt:
            self.positions.append(dict(member=member, due_date=when, amount=-debt))
        return dict(
            refund_cash=credit,
            refund_debt_offset=offset,
            recovered_overpayment=recovery,
            net_cash=regular_cash + credit - recovery,
        )

    def due(self, member, when):
        return [p for p in self.positions if p["member"] == member and p["due_date"] <= when]

    def snapshot(self, member):
        amounts = [p["amount"] for p in self.positions if p["member"] == member]
        claims = sum((max(ZERO, value) for value in amounts), ZERO)
        debt = -sum((min(ZERO, value) for value in amounts), ZERO)
        return dict(government_receivable=claims, government_overpayment_debt=debt)


def work_entries(rows):
    return [
        dict(
            member=r["member"],
            payment_month=r["payment_month"],
            known_date=r["known_date"],
            due_date=r["conditional_payment_date"],
            amount=r["closed_year_adjustment"],
        )
        for r in rows
        if r["closed_year_adjustment"]
    ]


def arf_entries(rows):
    return [
        dict(
            member=r["member"],
            payment_month=r["payment_month"],
            known_date=r["known_date"],
            due_date=r["conditional_payment_date"],
            amount=r["amount"],
        )
        for r in rows
        if r["arrears"] and r["amount"]
    ]
