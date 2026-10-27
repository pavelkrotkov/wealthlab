"""Reject contradictory identities, fiscal dates and unbounded allowance claims."""

import pytest

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import synthetic
from wealthlab.tax.spain_inputs import SpainCase


@pytest.mark.parametrize(
    "collection,index,field,value,match",
    [
        ("incomes", 0, "owner_id", "another_person", "case person"),
        ("assets", 0, "id", "general", "identifiers"),
        ("assets", 0, "exemption_eur", "9000000", "exceed"),
        ("assets", 0, "exemption_eur", "100", "cannot claim"),
        ("assets", 0, "treatment", "principal_home", "principal home"),
    ],
)
def test_invalid_owned_records_are_rejected(collection, index, field, value, match):
    data = synthetic().model_dump(mode="json")
    data[collection][index][field] = value
    with pytest.raises(ValueError, match=match):
        SpainCase.model_validate(data)


def test_future_year_needs_explicit_frozen_law_and_never_inherits_published_status():
    data = synthetic().model_dump(mode="json")
    data["year"] = 2026
    with pytest.raises(ValueError, match="frozen law"):
        SpainCase.model_validate(data)


@pytest.mark.parametrize(
    "field,value",
    [("general_reduction_eur", "50001"), ("long_held_gain_cap_exclusion_eur", "2001")],
)
def test_prelimited_reductions_and_cap_exclusions_still_cannot_exceed_their_base(field, value):
    data = synthetic().model_dump(mode="json")
    data[field] = value
    with pytest.raises(ValueError, match="cannot exceed"):
        evaluate(SpainCase.model_validate(data))


def test_exemption_with_progression_remains_blocked_until_its_rate_adapter_exists():
    data = synthetic().model_dump(mode="json")
    data["incomes"][0]["spanish_base"] = "exempt_with_progression"
    result = evaluate(SpainCase.model_validate(data))
    assert result["income"]["status"] == "blocked"
    assert "progression" in result["income"]["reasons"][0]
