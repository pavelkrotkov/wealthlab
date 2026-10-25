"""POMS RS02501.025/.080: full-year exemption, FRA-month cutoff and floor-dollar deductions.

The annual/monthly parameters are frozen2026 assumptions in future years.
Only current US W-2 earned wages are covered; special payments, foreign work,
self-employment and other auxiliary records require their own classifications.
"""

from decimal import ROUND_FLOOR, Decimal

from wealthlab.retirement.social_dates import full_retirement_month

LOWER = Decimal(24480)
HIGHER = Decimal(65160)
ZERO = Decimal(0)


def annual_deduction(person, year, wages):
    fra = full_retirement_month(person.birth_date)
    if year > fra.year:
        return ZERO
    if year == fra.year:
        earnings = sum(wages[: fra.month - 1], ZERO)
        exempt, divisor = HIGHER, Decimal(3)
    else:
        earnings = sum(wages, ZERO)
        exempt, divisor = LOWER, Decimal(2)
    return (max(ZERO, earnings - exempt) / divisor).to_integral_value(rounding=ROUND_FLOOR)


def monthly_exempt(person, year):
    fra = full_retirement_month(person.birth_date)
    return (HIGHER if year == fra.year else LOWER) / 12


def actual_wages(report):
    if report.actual_monthly_wages is None:
        raise ValueError("Realized wages must be supplied before assessing closed-year work.")
    return report.actual_monthly_wages
