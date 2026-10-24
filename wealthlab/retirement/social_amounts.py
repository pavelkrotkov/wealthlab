"""SSA source-backed dime arithmetic, early reductions and delayed-credit recognition."""

from datetime import date
from decimal import ROUND_FLOOR, Decimal, localcontext
from fractions import Fraction

from wealthlab.retirement.social_dates import alive, distance, seventieth_month


def dime(amount):
    return (amount * 10).to_integral_value(rounding=ROUND_FLOOR) / 10


def dollar(amount):
    return amount.to_integral_value(rounding=ROUND_FLOOR)


def pia(person, month, cola):
    """January-2026 PIA already includes December-2025 COLA.

    Later assumed COLAs change December entitlement, paid the following January.
    Truncate each year's PIA to a dime rather than rounding only the final power.
    """
    return project_pia(person.pia_january_2026, month, cola)


def project_pia(amount, month, cola):
    count = max(0, month.year - 2026 + int(month.month == 12))
    for _ in range(count):
        amount = dime(amount * (1 + cola))
    return amount


def reduced(amount, months_early, spouse=False):
    with localcontext() as context:
        context.prec = 50
        denominator = 3600 if spouse else 900
        numerator = 25 if spouse else 5
        reduction = Fraction(min(36, months_early) * numerator, denominator)
        reduction += Fraction(max(0, months_early - 36) * 5, 1200)
        return dime(amount * (reduction.denominator - reduction.numerator) / reduction.denominator)


def delayed_amount(person, fra, month, unreduced):
    end = min(person.claim_month, seventieth_month(person.birth_date))
    if month.year == person.claim_month.year and month < seventieth_month(person.birth_date):
        end = min(end, date(person.claim_month.year, 1, 1))
    credits = max(0, distance(fra, end))
    # Supported birth cohort (after January1,1943): 2/3 percent per month.
    return dime(unreduced * credits / 150)


def own_amount(person, fra, month, unreduced):
    if month < person.claim_month or not person.own_insured or not alive(person, month):
        return Decimal(0), Decimal(0)
    early = max(0, distance(person.claim_month, fra))
    base = reduced(unreduced, early)
    return base, base + delayed_amount(person, fra, month, unreduced)
