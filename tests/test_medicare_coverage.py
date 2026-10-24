"""Enrollment starts at the supplied date; IRMAA only applies to an enrolled coverage part."""

import pytest

from tests.test_medicare_cash import calculate, payload


def test_part_a_only_needs_no_income_history_and_uses_supplied_premium():
    data = payload()
    data.update(income_history=[], coverage=[data["coverage"][0]])
    data["coverage"][0].update(
        part_a_monthly_2026=311,
        part_b=False,
        part_d=False,
        part_d_plan_monthly_2026=0,
        other_monthly_health_cost_2026=0,
    )
    result = calculate(data)
    assert result["total_due"] == 24 * 311
    assert result["monthly"][0]["magi"] is None
    assert result["monthly"][0]["part_b"] == result["monthly"][0]["part_d"] == 0


@pytest.mark.parametrize("part", ["part_b", "part_d"])
def test_income_surcharge_does_not_charge_a_part_without_enrollment(part):
    data = payload()
    data["coverage"][0][part] = False
    if part == "part_d":
        data["coverage"][0]["part_d_plan_monthly_2026"] = 0
    first = calculate(data)["monthly"][0]
    assert first[part] == 0
    key = "b_irmaa" if part == "part_b" else "d_irmaa"
    assert first[key] == 0
