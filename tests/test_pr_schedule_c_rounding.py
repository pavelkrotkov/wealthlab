"""ScheduleC's rounded country percentage and separate total limit can bind differently."""

from decimal import Decimal

from wealthlab.tax.pr_credit_limit import limited


def test_downward_country_percentage_changes_actual_credit_from_3333_33_to_3333():
    result = limited(Decimal(10000), Decimal(9000), Decimal(1), Decimal(3))
    assert result["allowed"] == Decimal("3333.00")
    assert result["limitation_fraction"] == Decimal(".3333")


def test_upward_country_percentage_cannot_exceed_unrounded_aggregate_limit():
    result = limited(Decimal(10000), Decimal(9000), Decimal(2), Decimal(3))
    assert result["limitation"] == Decimal("6667.00")
    assert result["total_limitation"] == result["allowed"] == Decimal("6666.67")
