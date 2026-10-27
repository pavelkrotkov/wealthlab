"""Independent EUR4m owned-wealth arithmetic with ample income and no wealth cap reduction."""

from decimal import Decimal

import pytest
from spain_regional_cases import case

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_inputs import SpainCase


@pytest.mark.parametrize(
    ("region", "minimum", "gross"),
    [
        ("balearic", "3000000", "7473.49"),
        ("valencia", "1000000", "39166.32"),
        ("asturias", "700000", "41729.48"),
    ],
)
def test_custom_minimum_and_scale_change_actual_assessment(region, minimum, gross):
    result = evaluate(SpainCase.model_validate(case(region)))["wealth"]["assessment"]
    assert result["wealth_minimum"] == Decimal(minimum)
    assert result["wealth"]["gross_quota"] == Decimal(gross)
    assert result["wealth_liability"] == Decimal(gross)
    assert result["solidarity_liability"] == Decimal("5100")
