"""Galicia's coupled relief is an explicit prelimited fact, never an invented fixed point."""

from decimal import Decimal

from spain_regional_cases import case

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_inputs import SpainCase


def test_unknown_galicia_relief_blocks_only_wealth():
    result = evaluate(SpainCase.model_validate(case("galicia")))
    assert result["income"]["status"] == "conditional"
    assert result["wealth"]["status"] == "blocked"
    assert result["total_liability_eur"] is None


def test_galicia_requires_supplied_final_relief_after_solidarity_offset():
    data = case("galicia")
    data["credits"].update(
        wealth_regional="1000",
        regional_bonus_included_confirmed=True,
        source="Synthetic independently prelimited total relief after Galicia solidarity offset",
    )
    result = evaluate(SpainCase.model_validate(data))["wealth"]["assessment"]
    assert result["wealth_liability"] == Decimal("35546.37")
    assert result["regional_bonus"] == 0
    assert result["solidarity_liability"] == Decimal("5100")
