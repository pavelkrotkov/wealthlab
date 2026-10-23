"""Shares sold and ending market-value weights measure different decisions."""

from collections import defaultdict
from decimal import Decimal

from wealthlab.household.calendar import money


def summarize(case, book, values, wealth):
    original = defaultdict(Decimal)
    remaining_original = defaultdict(Decimal)
    remaining = defaultdict(Decimal)
    for lot in case.lots:
        original[lot.security_id] += lot.quantity

    opening_ids = {lot.id for lot in case.lots}
    for lot in book.lots.values():
        remaining[lot.security_id] += lot.quantity
        if book.origins[lot.id] in opening_ids:
            remaining_original[lot.security_id] += lot.quantity
    records = []
    groups = defaultdict(Decimal)
    for security in case.securities:
        key = security.id
        sold = original[key] - remaining_original[key]
        groups[security.exposure_group] += values[key]
        records.append(
            dict(
                security=key,
                original_units=original[key],
                original_units_sold=sold,
                original_fraction_sold=ratio(sold, original[key]),
                remaining_units=remaining[key],
                market_value=money(values[key]),
                wealth_fraction=ratio(values[key], wealth),
            )
        )
    return dict(
        securities=records,
        exposure_groups=[
            dict(group=key, market_value=money(value), wealth_fraction=ratio(value, wealth))
            for key, value in groups.items()
        ],
        meaning="Market-value weights of configured long-only holdings, including cash in wealth. "
        "These are not beta, look-through issuer exposure or derivative-adjusted exposure.",
    )


def ratio(value, total):
    return value / total if total else None
