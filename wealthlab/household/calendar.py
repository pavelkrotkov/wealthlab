"""Calendar-month accruals with exact overlap for partial months and retirement."""

from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from wealthlab.household.schedules import DatedAmount

if TYPE_CHECKING:
    from wealthlab.household.scenario import Scenario

CENT = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(CENT)


def months(start: date, end: date):
    cursor = start
    while cursor < end:
        following = date(cursor.year + cursor.month // 12, cursor.month % 12 + 1, 1)
        yield cursor, min(following, end)
        cursor = following


def fraction(start: date, end: date) -> Decimal:
    return Decimal((end - start).days) / monthrange(start.year, start.month)[1]


def amount(item: DatedAmount, start: date, end: date, scenario: Scenario) -> Decimal:
    left, right = max(item.start, start), min(item.end, end)
    if right <= left:
        return Decimal(0)
    elapsed = (date(start.year, start.month, 1) - scenario.start).days / 365.25
    growth = Decimal(str((1 + item.annual_growth) ** max(0, elapsed)))
    rate = Decimal(str(scenario.usd_per_currency[item.currency]))
    return money(item.monthly_amount * rate * growth * fraction(left, right))
