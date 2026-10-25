"""Charge only eligible pre-FRA months; the initial non-service year is not elective."""

from decimal import Decimal

from wealthlab.retirement.social_dates import full_retirement_month
from wealthlab.retirement.social_work_rules import annual_deduction, monthly_exempt

ZERO = Decimal(0)


def eligible(person, row, fra):
    when = row["entitlement_month"]
    return person.own_insured and person.claim_month <= when < fra


def assess(person, year, wages, rows, grace_used, whole_month):
    fra = full_retirement_month(person.birth_date)
    limit = monthly_exempt(person, year)
    grace = not grace_used and any(
        eligible(person, r, fra) and wages[r["entitlement_month"].month - 1] <= limit for r in rows
    )
    remaining = annual_deduction(person, year, wages)
    initial = remaining
    amounts = []
    for row in rows:
        amount = charge(person, row, fra, wages, limit, grace, remaining)
        remaining -= amount
        cash_held = row["issued_before_offsets"] if whole_month and amount else amount
        amounts.append(dict(deduction=amount, cash_held=cash_held))
    return dict(
        annual_excess=initial,
        grace_year=grace,
        grace_used=grace_used or grace,
        uncharged_excess=remaining,
        months=amounts,
    )


def charge(person, row, fra, wages, limit, grace, remaining):
    if not eligible(person, row, fra):
        return ZERO
    if grace and wages[row["entitlement_month"].month - 1] <= limit:
        return ZERO
    return min(remaining, row["issued_before_offsets"])
