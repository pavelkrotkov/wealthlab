"""The premium year uses its own lookback return, not the current retirement income."""

from decimal import Decimal

import pytest

from tests.test_medicare_cash import calculate, payload


def test_joint_magi_and_tax_exempt_interest_are_not_split_between_spouses():
    data = payload()
    data["income_history"][0].update(agi=218000, tax_exempt_interest=1)
    rows = calculate(data)["monthly"]
    first = rows[0]
    spouse = next(row for row in rows if row["member"] == "spouse")
    assert first["magi"] == spouse["magi"] == 218001
    assert first["b_irmaa"] == spouse["b_irmaa"] == Decimal("81.20")
    assert first["income_year"] == 2024


def test_lower_prior_year_income_changes_next_year_not_current_costs():
    result = calculate(payload())
    first = result["monthly"][0]
    following = next(row for row in result["monthly"] if row["date"].year == 2027)
    assert first["part_b"] == Decimal("405.80")
    assert first["d_irmaa"] == Decimal("37.50")
    assert following["part_b"] == Decimal("202.90")
    assert following["d_irmaa"] == 0
    assert following["income_year"] == 2025


def test_missing_lookback_fails_instead_of_defaulting_to_zero_irmaa():
    data = payload()
    data["income_history"] = []
    with pytest.raises(ValueError, match="Missing two-year"):
        calculate(data)
