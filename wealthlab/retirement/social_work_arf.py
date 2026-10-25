"""Actual full/partial work deductions credit the own-record reduction factor at FRA.

The supplied processing month is an administrative cash assumption. Earlier
increases remain receivables once the FRA year closes, never spendable cash.
"""

from datetime import date
from decimal import Decimal

from wealthlab.retirement.social_amounts import dollar, pia, reduced
from wealthlab.retirement.social_dates import distance, full_retirement_month

ZERO = Decimal(0)


def adjustments(case, baseline, assessed):
    people = {person.id: person for person in case.claims.members}
    credits = credited_months(people, assessed)
    entries = []
    for row in baseline["monthly_entitlements"]:
        person = people[row["member"]]
        fra = full_retirement_month(person.birth_date)
        early = max(0, distance(person.claim_month, fra))
        if not credits[person.id] or row["entitlement_month"] < fra or not early:
            continue
        extra = increase(case, person, row, early, credits[person.id])
        entries.append(arf_entry(case.work, row, fra, extra, credits[person.id]))
    return entries


def increase(case, person, row, early, credits):
    updated = dollar(
        reduced(
            pia(person, row["entitlement_month"], case.claims.future_cola_assumption),
            max(0, early - credits),
        )
    )
    return max(ZERO, updated - row["issued_before_offsets"])


def arf_entry(policy, row, fra, amount, credits):
    processed = date(fra.year + 1, policy.arf_payment_month_following_fra_year, 1)
    return dict(
        member=row["member"],
        entitlement_month=row["entitlement_month"],
        payment_month=row["payment_month"],
        amount=amount,
        crediting_months=credits,
        known_date=date(fra.year + 1, 1, 1),
        conditional_payment_date=max(processed, row["payment_month"]),
        arrears=row["payment_month"] < processed,
    )


def credited_months(people, assessed):
    return {
        member: sum(row["crediting_month"] for row in assessed if row["member"] == member)
        for member in people
    }
