"""Unsupported coverage and conflicting history cannot become apparently cheap healthcare."""

import pytest

from tests.test_medicare_cash import calculate, payload


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("eligibility_confirmed", False),
        ("standard_b_premium_applicable", False),
        ("start", "2026-01-02"),
        ("end", "2028-01-02"),
        ("member", "unknown"),
        ("provenance", "unresolved"),
    ],
)
def test_unsupported_or_ambiguous_coverage_fails(field, value):
    data = payload()
    data["coverage"][0][field] = value
    with pytest.raises(ValueError):
        calculate(data)


def test_coverage_cannot_overlap_but_adjacent_periods_can_change_costs():
    data = payload()
    second = {**data["coverage"][0], "id": "second_period", "start": "2027-01-01"}
    data["coverage"].append(second)
    with pytest.raises(ValueError, match="cannot overlap"):
        calculate(data)
    data["coverage"][0]["end"] = "2027-01-01"
    assert len(calculate(data)["monthly"]) == 42


def test_conflicting_returns_or_determinations_are_rejected():
    data = payload()
    data["income_history"].append({**data["income_history"][0], "id": "duplicate"})
    with pytest.raises(ValueError, match="one income return"):
        calculate(data)


def test_individual_return_cannot_be_shared_as_two_peoples_income_history():
    data = payload()
    data["income_history"][0]["filing"] = "individual"
    with pytest.raises(ValueError, match="Only a joint return"):
        calculate(data)
