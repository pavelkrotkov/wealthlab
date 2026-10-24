"""A redetermination is a conditional SSA decision, never automatic retirement relief.

The older-return fallback is unavailable once the normal lookback return is
present. One spouse's explicit determination does not replace the other's.
"""

from decimal import Decimal

import pytest

from tests.test_medicare_cash import calculate, payload


def test_explicit_three_year_fallback_requires_missing_two_year_return():
    data = payload()
    older = {**data["income_history"][0], "id": "older", "year": 2023}
    data["income_history"].append(older)
    data["determinations"] = [
        dict(
            id="fallback",
            member="person",
            premium_year=2026,
            income="older",
            method="three_year_fallback_confirmed",
            provenance="assumption",
        )
    ]
    with pytest.raises(ValueError, match="cannot replace available"):
        calculate(data)
    data["income_history"][0]["members"] = ["spouse"]
    first = calculate(data)["monthly"][0]
    assert first["income_year"] == 2023
    assert first["determination"] == "three_year_fallback_confirmed"


def test_redetermination_is_explicit_and_does_not_change_the_other_spouse():
    data = payload()
    data["determinations"] = [
        dict(
            id="conditional",
            member="person",
            premium_year=2026,
            income="joint_2025",
            method="conditional_ssa_redetermination",
            provenance="assumption",
        )
    ]
    rows = calculate(data)["monthly"]
    assert rows[0]["b_irmaa"] == 0
    assert rows[0]["determination"] == "conditional_ssa_redetermination"
    spouse = next(row for row in rows if row["member"] == "spouse")
    assert spouse["b_irmaa"] == Decimal("202.90")
