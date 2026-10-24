"""Invalid premium histories or enrollment flags fail before cash can be projected."""

import pytest

from tests.test_medicare_cash import calculate, payload


@pytest.mark.parametrize(
    ("field", "value"),
    [("complete_context", False), ("end_year", 2026), ("premium_growth", "0.01")],
)
def test_invalid_case_assumptions_are_rejected(field, value):
    data = payload()
    data[field] = value
    with pytest.raises(ValueError):
        calculate(data)


@pytest.mark.parametrize(("field", "value"), [("part_a", False), ("part_d", False)])
def test_a_missing_coverage_part_cannot_charge_its_premium(field, value):
    data = payload()
    data["coverage"][0]["part_a_monthly_2026"] = 311
    data["coverage"][0][field] = value
    with pytest.raises(ValueError, match="Unenrolled Medicare"):
        calculate(data)


def test_missing_all_parts_and_outside_projection_cash_are_rejected():
    data = payload()
    data["coverage"][0].update(part_a=False, part_b=False, part_d=False)
    with pytest.raises(ValueError, match="at least one"):
        calculate(data)
    data = payload()
    data["receipts"][0]["date"] = "2028-01-01"
    with pytest.raises(ValueError, match="cash receipts"):
        calculate(data)


@pytest.mark.parametrize(
    "method", ["three_year_fallback_confirmed", "conditional_ssa_redetermination"]
)
def test_wrong_income_year_cannot_be_used_as_an_explicit_determination(method):
    data = payload()
    data["determinations"] = [
        dict(
            id="invalid",
            member="person",
            premium_year=2026,
            income="joint_2024",
            method=method,
            provenance="assumption",
        )
    ]
    with pytest.raises(ValueError):
        calculate(data)
