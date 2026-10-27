"""Original foreign-tax vintages retain person, basket, age and unresolved disposition.

Current foreign tax uses the current-year source limit first. Earlier vintages
then use remaining capacity in original-year order. Generated excess retains
its current origin year. A prior carryback review and a joint-person allocation
are independent requirements before claiming a forward-only conclusion.
"""

from decimal import Decimal

ZERO = Decimal(0)


def use_carries(case, basket, capacity, used):
    total, year = ZERO, case.annual.policy.year
    for carry in sorted(case.opening_carries, key=lambda c: (c.origin_year, c.id)):
        if carry.basket == basket and year - carry.origin_year <= 10:
            amount = min(carry.available_usd, capacity - total)
            used[carry.id] = amount
            total += amount
    return total


def carry_disposition(case, audit, used):
    excess = generated(case, audit)
    return dict(
        opening=opening(case, used),
        generated_excess=excess,
        status=status(case, excess),
        prior_year_cash_refund_assumed=ZERO,
    )


def opening(case, used):
    year = case.annual.policy.year
    return [
        dict(
            id=c.id,
            owner_id=c.owner_id,
            origin_year=c.origin_year,
            basket=c.basket,
            used=used.get(c.id, ZERO),
            expired=year - c.origin_year > 10,
            remaining=ZERO if year - c.origin_year > 10 else c.available_usd - used.get(c.id, ZERO),
        )
        for c in case.opening_carries
    ]


def generated(case, audit):
    year = case.annual.policy.year
    owner = next(iter(case.people)) if len(case.people) == 1 else None
    return [
        dict(
            id=f"generated_{year}_{row['basket']}",
            owner_id=owner,
            filing_unit_members=list(case.people),
            origin_year=year,
            basket=row["basket"],
            amount=row["excess_current"],
            expires_after=year + 10,
        )
        for row in audit
        if row["excess_current"]
    ]


def status(case, excess):
    if not excess:
        return "conditional_forward_vintages"
    if len(case.people) > 1:
        return "joint_person_allocation_required"
    if case.prior_year_carryback_capacity_reviewed_zero_confirmed:
        return "conditional_forward_vintages"
    return "prior_carryback_review_required"
