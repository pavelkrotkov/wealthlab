"""Supplied special minima require provenance and a supported regional statutory amount."""

from decimal import Decimal

import pytest
from spain_regional_cases import case

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_inputs import SpainCase


def test_supplied_andalusia_special_minimum_does_not_infer_disability_eligibility():
    data = case("andalusia")
    data["wealth_allowance"] = dict(
        minimum_eur="1250000",
        eligibility_source="Synthetic independently supplied eligible special minimum",
    )
    wealth = evaluate(SpainCase.model_validate(data))["wealth"]["assessment"]
    assert wealth["wealth_minimum"] == Decimal("1250000")
    assert wealth["wealth_taxable_base"] == Decimal("2750000")
    assert "independently supplied" in wealth["supplied_wealth_allowance"]["eligibility_source"]


def test_unsupported_supplied_minimum_blocks_only_wealth():
    data = case("madrid")
    data["wealth_allowance"] = dict(minimum_eur="9999999", eligibility_source="Unverified request")
    result = evaluate(SpainCase.model_validate(data))
    assert result["income"]["status"] == "conditional"
    assert result["wealth"]["status"] == "blocked"
    assert result["total_liability_eur"] is None


def test_special_minimum_without_source_is_invalid():
    data = case("andalusia")
    data["wealth_allowance"] = dict(minimum_eur="1250000", eligibility_source="")
    with pytest.raises(ValueError, match="eligibility_source"):
        SpainCase.model_validate(data)
