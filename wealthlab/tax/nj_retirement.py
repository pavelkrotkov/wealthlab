"""Full-year NJ pension exclusion and Worksheet D; eligible income is owner-specific."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.household.records import Money
from wealthlab.tax.facts import TaxModel


class RetirementEligibility(TaxModel):
    # Pension qualification includes age 62 or qualifying disability. Other
    # retirement qualification requires age 62; disability alone is insufficient.
    qualified_pension: Money = Decimal(0)
    age62_other_income: Money = Decimal(0)
    special_exclusion_eligible: bool = False


def maximum(total: Decimal, base: Decimal, status: str) -> Decimal:
    """Pension uses pension as base; Worksheet D uses total NJ income instead."""
    limit = {"joint": 100000, "separate": 50000}.get(status, 75000)
    if total <= 100000:
        return Decimal(limit)
    if total <= 125000:
        return base * Decimal(limit) / 200000
    if total <= 150000:
        return base * Decimal(limit) / 400000
    return Decimal(0)


def exclusions(
    total: Decimal,
    pension: Decimal,
    employment: Decimal,
    eligible: RetirementEligibility,
    status: str,
) -> dict:
    """Explicit eligible-owner amounts prevent excluding a younger spouse's income.

    Caller establishes age/disability and ownership; these already-qualified
    amounts are not inferred from the older spouse or the household total.
    """
    if eligible.qualified_pension > pension or eligible.age62_other_income > total - pension:
        raise ValueError("Eligible retirement amounts exceed their NJ income categories.")
    pension_exclusion = min(eligible.qualified_pension, maximum(total, pension, status))
    unused = max(Decimal(0), maximum(total, total, status) - pension_exclusion)
    other = min(eligible.age62_other_income, unused) if employment <= 3000 else Decimal(0)
    special = Decimal(0)
    if eligible.special_exclusion_eligible:
        special = Decimal(3000 if status in {"single", "separate"} else 6000)
    # Special exclusion is independent of pension/unused caps and can reduce
    # remaining pension income; it is not limited to non-pension income.
    other = min(total - pension_exclusion, other + special)
    return dict(pension_exclusion=money(pension_exclusion), other_exclusion=money(other))
