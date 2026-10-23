"""2025 NJ-1040 tables A/B; taxable income, before credits and filing threshold."""

from decimal import ROUND_HALF_UP, Decimal

from wealthlab.household.calendar import money

# Published rate/offset schedules, not integrated marginal brackets: Table B
# contains a fifty-cent discontinuity at $70,000 that must be preserved.
TABLE_A = (
    (20_000, ".014", "0"),
    (35_000, ".0175", "70"),
    (40_000, ".035", "682.50"),
    (75_000, ".05525", "1492.50"),
    (500_000, ".0637", "2126.25"),
    (1_000_000, ".0897", "15126.25"),
    (float("inf"), ".1075", "32926.25"),
)
TABLE_B = (
    (20_000, ".014", "0"),
    (50_000, ".0175", "70"),
    (70_000, ".0245", "420"),
    (80_000, ".035", "1154.50"),
    (150_000, ".05525", "2775"),
    (500_000, ".0637", "4042.50"),
    (1_000_000, ".0897", "17042.50"),
    (float("inf"), ".1075", "34842.50"),
)


def tax(taxable: Decimal, status: str) -> Decimal:
    """Under $100k use the $50-band midpoint and whole-dollar table rounding."""
    validate(taxable, status)
    table = TABLE_A if status in {"single", "separate"} else TABLE_B
    base = taxable // 50 * 50 + 25 if taxable < 100_000 else taxable
    _ceiling, rate, offset = next(row for row in table if base <= row[0])
    result = base * Decimal(rate) - Decimal(offset)
    result -= table_correction(base, status)
    return (
        result.quantize(Decimal(1), rounding=ROUND_HALF_UP) if taxable < 100_000 else money(result)
    )


def validate(taxable: Decimal, status: str) -> None:
    if status not in {"single", "separate", "joint", "head", "surviving"}:
        raise ValueError("Unknown NJ filing status.")
    if not taxable.is_finite() or taxable < 0:
        raise ValueError("Taxable income must be finite and nonnegative.")


def table_correction(base: Decimal, status: str) -> Decimal:
    # The published under-$100k table uses the continuous $1,155 offset
    # in this band, although the printed rate schedule says $1,154.50.
    if status in {"joint", "head", "surviving"} and 70_000 < base < 80_000:
        return Decimal("0.50")
    return Decimal(0)
