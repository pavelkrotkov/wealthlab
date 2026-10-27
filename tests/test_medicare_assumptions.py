"""Premium inflation and threshold inflation are separate conditional future assumptions."""

from decimal import Decimal

from tests.test_medicare_cash import calculate, payload


def test_future_growth_is_an_explicit_assumption_and_does_not_change_2026():
    data = payload()
    data.update(future_policy="index_2026_assumption", premium_growth="0.10", threshold_growth=0)
    rows = calculate(data)["monthly"]
    first = rows[0]
    following = next(row for row in rows if row["date"].year == 2027)
    assert first["total_due"] == Decimal("683.30")
    assert following["total_due"] == Decimal("487.19")
    assert following["rule_mode"] == "index_2026_assumption"


def test_threshold_growth_changes_future_brackets_separately_from_premiums():
    data = payload()
    data["income_history"][1].update(agi=220000, tax_exempt_interest=0)
    data.update(future_policy="index_2026_assumption", premium_growth=0, threshold_growth="0.02")
    rows = calculate(data)["monthly"]
    following = next(row for row in rows if row["date"].year == 2027)
    assert following["b_irmaa"] == 0
    assert following["part_b"] == Decimal("202.90")
