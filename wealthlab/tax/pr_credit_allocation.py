"""ScheduleC PartI uses a rounded percentage before allocating unassigned exemptions.

Two decimal percentage points means four decimal places in the unit fraction.
The later PartIV jurisdiction limit repeats that rounding on net income; its
separate aggregate limitation retains the unrounded total fraction. Monetary
products keep the household engine's existing cent precision.
"""

from decimal import ROUND_HALF_UP, Decimal

from wealthlab.household.calendar import money

ZERO, ONE = Decimal(0), Decimal(1)


def fraction(numerator, denominator):
    return min(ONE, max(ZERO, numerator) / denominator) if denominator > 0 else ZERO


def percentage(numerator, denominator):
    return fraction(numerator, denominator).quantize(Decimal(".0001"), rounding=ROUND_HALF_UP)


def allocation(gross, source_gross, deductions):
    share = percentage(source_gross, gross)
    assigned = money(deductions * share)
    return dict(
        source_gross=source_gross,
        all_source_gross=gross,
        deductions_and_exemptions=deductions,
        attributable_percentage=share,
        allocated_deductions_and_exemptions=assigned,
        source_net=max(ZERO, source_gross - assigned),
    )
